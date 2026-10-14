#!/usr/bin/env python3
"""학습 서비스 CLI + 로컬 웹 퀴즈 서버 (표준 라이브러리만 사용).

  python3 tools/study.py new-topic <slug> --title "<제목>"
  python3 tools/study.py import-md <slug> <file.md> [...]
  python3 tools/study.py add-questions <slug> <new.json>
  python3 tools/study.py validate <slug>
  python3 tools/study.py serve [--port 8765]
  python3 tools/study.py due <slug> [--limit N] [--json]
  python3 tools/study.py record <slug> <responses.json>
  python3 tools/study.py stats <slug> [--json]

비공개 데이터는 local/topics/<slug>/ 에, 공개 노트는 docs/topics/<slug>/ 에 둔다.
SRS 규칙은 .claude/skills/spaced-repetition/SKILL.md 와 일치해야 한다.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import threading
from collections import defaultdict
from datetime import date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
LOCAL = ROOT / "local" / "topics"
DOCS = ROOT / "docs" / "topics"
QUIZ_HTML = ROOT / "tools" / "quiz" / "index.html"

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SESSION_RE = re.compile(r"^\d{8}-\d{6}(?:-[a-z0-9]+)?$")
TYPES = {"single", "multi", "short"}
CONFIDENCES = ("sure", "unsure", "guess")
BLOOMS = {"remember", "understand", "apply", "analyze", "evaluate", "create"}
QUALITY = {  # (정답 여부, 확신도) -> SM-2 응답 품질
    (True, "sure"): 5, (True, "unsure"): 4, (True, "guess"): 3,
    (False, "guess"): 2, (False, "unsure"): 1, (False, "sure"): 0,
}

_write_lock = threading.Lock()


class StudyError(Exception):
    pass


# ---------------------------------------------------------------- 파일 입출력

def topic_dir(slug: str) -> Path:
    if not SLUG_RE.match(slug):
        raise StudyError(f"잘못된 slug: {slug!r} (소문자·숫자·하이픈만)")
    return LOCAL / slug


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_bank(slug: str) -> dict:
    path = topic_dir(slug) / "questions.json"
    if not path.exists():
        raise StudyError(f"문제 은행 없음: {path.relative_to(ROOT)} (new-topic 먼저)")
    return read_json(path, None)


def save_bank(slug: str, bank: dict) -> None:
    write_json(topic_dir(slug) / "questions.json", bank)


def load_srs(slug: str) -> dict:
    return read_json(topic_dir(slug) / "srs.json", {})


def load_attempts(slug: str) -> list[dict]:
    adir = topic_dir(slug) / "attempts"
    return [read_json(p, None) for p in sorted(adir.glob("*.json"))] if adir.exists() else []


def list_topics() -> list[str]:
    if not LOCAL.exists():
        return []
    return sorted(p.name for p in LOCAL.iterdir() if (p / "questions.json").exists())


def concept_ids_from_research(slug: str) -> set[str] | None:
    """01_research.md 의 '## 개념 맵' 표 첫 열에서 개념 ID를 읽는다. 파일이 없으면 None."""
    path = topic_dir(slug) / "01_research.md"
    if not path.exists():
        return None
    ids, in_map = set(), False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_map = line.strip() == "## 개념 맵"
            continue
        if in_map and line.startswith("|"):
            cell = line.strip("|").split("|")[0].strip().strip("`")
            if SLUG_RE.match(cell):
                ids.add(cell)
    return ids


# ---------------------------------------------------------------- 검증·채점

def validate_question(q: dict, concept_ids: set[str] | None = None) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    qid = q.get("id", "?")
    qtype = q.get("type")
    if qtype not in TYPES:
        errors.append(f"{qid}: type은 {sorted(TYPES)} 중 하나")
    if not str(q.get("stem", "")).strip():
        errors.append(f"{qid}: stem 비어 있음")
    answer = q.get("answer")
    if not isinstance(answer, list) or not answer or not all(isinstance(a, str) and a.strip() for a in answer):
        errors.append(f"{qid}: answer는 비어 있지 않은 문자열 배열")
        answer = []
    if qtype in ("single", "multi"):
        choices = q.get("choices")
        if not isinstance(choices, dict) or len(choices) < 2:
            errors.append(f"{qid}: choices는 2개 이상의 {{키: 내용}}")
        else:
            keys = list(choices)
            expected = [chr(ord("A") + i) for i in range(len(keys))]
            if keys != expected:
                errors.append(f"{qid}: choices 키는 {''.join(expected)} 순서여야 함 (현재 {''.join(keys)})")
            missing = [a for a in answer if a not in choices]
            if missing:
                errors.append(f"{qid}: 정답 {missing}이 choices에 없음")
            for k in q.get("why_wrong") or {}:
                if k not in choices or k in answer:
                    warnings.append(f"{qid}: why_wrong 키 {k}는 오답 선택지가 아님")
        if qtype == "single" and len(answer) != 1:
            errors.append(f"{qid}: single은 정답 1개 (현재 {len(answer)})")
        if qtype == "multi" and len(answer) < 2:
            errors.append(f"{qid}: multi는 정답 2개 이상")
        if len(set(answer)) != len(answer):
            errors.append(f"{qid}: 정답 중복")
    if "explanation" not in q:
        errors.append(f"{qid}: explanation 필드 없음 (빈 문자열 허용)")
    elif not str(q["explanation"]).strip():
        warnings.append(f"{qid}: 해설 비어 있음")
    concepts = q.get("concepts")
    if not isinstance(concepts, list):
        errors.append(f"{qid}: concepts는 배열")
    elif not concepts:
        warnings.append(f"{qid}: 개념 태그 없음")
    elif concept_ids is not None:
        unknown = [c for c in concepts if c not in concept_ids]
        if unknown:
            warnings.append(f"{qid}: 개념 맵에 없는 ID {unknown}")
    if "difficulty" in q and q["difficulty"] not in (1, 2, 3):
        errors.append(f"{qid}: difficulty는 1~3")
    if "bloom" in q and q["bloom"] not in BLOOMS:
        errors.append(f"{qid}: bloom은 {sorted(BLOOMS)} 중 하나")
    if not str(q.get("source", "")).strip():
        errors.append(f"{qid}: source 비어 있음")
    return errors, warnings


def validate_bank(slug: str, bank: dict) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    concept_ids = concept_ids_from_research(slug)
    seen = set()
    for q in bank.get("questions", []):
        qid = q.get("id")
        if not isinstance(qid, str) or not re.match(r"^q\d{3,}$", qid):
            errors.append(f"{qid}: id는 q + 숫자 3자리 이상")
        elif qid in seen:
            errors.append(f"{qid}: id 중복")
        seen.add(qid)
        e, w = validate_question(q, concept_ids)
        errors += e
        warnings += w
    return errors, warnings


def normalize_text(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip().lower()


def grade(q: dict, selected: list[str] | None, text: str | None) -> bool:
    if q["type"] == "short":
        given = normalize_text(text or (selected or [""])[0])
        return given != "" and given in {normalize_text(a) for a in q["answer"]}
    return sorted(set(selected or [])) == sorted(q["answer"])


def srs_update(state: dict | None, correct: bool, confidence: str, today: date) -> dict:
    s = dict(state or {"ef": 2.5, "interval": 0, "reps": 0, "lapses": 0, "history": []})
    q = QUALITY[(correct, confidence)]
    if q < 3:
        s["reps"], s["interval"] = 0, 1
        s["lapses"] = s.get("lapses", 0) + 1
    else:
        s["reps"] += 1
        s["interval"] = 1 if s["reps"] == 1 else 3 if s["reps"] == 2 else round(s["interval"] * s["ef"])
    s["ef"] = round(max(1.3, s["ef"] + 0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)), 2)
    s["due"] = (today + timedelta(days=s["interval"])).isoformat()
    s["history"] = s.get("history", []) + [
        {"date": today.isoformat(), "correct": correct, "confidence": confidence, "q": q}
    ]
    return s


def public_question(q: dict) -> dict:
    """웹 UI로 보낼 문항 (정답·해설 제외)."""
    out = {k: q[k] for k in ("id", "type", "stem", "choices", "concepts", "domain", "difficulty") if k in q}
    if q["type"] == "multi":
        out["pick"] = len(q["answer"])
    return out


def feedback(q: dict, correct: bool) -> dict:
    return {
        "correct": correct,
        "answer": q["answer"],
        "explanation": q.get("explanation", ""),
        "why_wrong": q.get("why_wrong", {}),
        "concepts": q.get("concepts", []),
        "flag": q.get("flag"),
    }


def record_response(slug: str, session_id: str, resp: dict, mode: str, source: str, bank: dict | None = None) -> dict:
    """응답 하나를 채점하고 attempts/<session>.json 과 srs.json 에 기록한다."""
    if not SESSION_RE.match(session_id):
        raise StudyError(f"잘못된 session id: {session_id!r}")
    bank = bank or load_bank(slug)
    by_id = {q["id"]: q for q in bank["questions"]}
    qid = resp.get("qid")
    if qid not in by_id:
        raise StudyError(f"없는 문항: {qid!r}")
    confidence = resp.get("confidence", "unsure")
    if confidence not in CONFIDENCES:
        raise StudyError(f"confidence는 {CONFIDENCES} 중 하나")
    q = by_id[qid]
    selected = [str(s).upper() for s in resp.get("selected") or []]
    text = resp.get("text")
    correct = grade(q, selected, text)
    now = datetime.now()
    entry = {
        "qid": qid, "selected": selected, "text": text, "correct": correct,
        "confidence": confidence, "seconds": int(resp.get("seconds") or 0),
        "answered_at": now.isoformat(timespec="seconds"),
    }
    tdir = topic_dir(slug)
    with _write_lock:
        apath = tdir / "attempts" / f"{session_id}.json"
        attempt = read_json(apath, None) or {
            "topic": slug, "session": session_id, "mode": mode, "source": source,
            "started_at": now.isoformat(timespec="seconds"), "responses": [],
        }
        attempt["responses"].append(entry)
        attempt["finished_at"] = now.isoformat(timespec="seconds")
        write_json(apath, attempt)
        srs = load_srs(slug)
        srs[qid] = srs_update(srs.get(qid), correct, confidence, now.date())
        write_json(tdir / "srs.json", srs)
    return {**feedback(q, correct), "next_due": srs[qid]["due"]}


def new_session_id(suffix: str = "") -> str:
    sid = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{sid}-{suffix}" if suffix else sid


# ---------------------------------------------------------------- 출제 순서·통계

def pick_questions(slug: str, mode: str = "due", limit: int = 20, concept: str | None = None) -> list[dict]:
    """mode: due(복습 예정→새 문항→나머지) | new | wrong | all | random"""
    import random

    bank = load_bank(slug)
    srs = load_srs(slug)
    today = date.today().isoformat()
    qs = [q for q in bank["questions"] if not concept or concept in q.get("concepts", [])]

    def last_wrong(q):
        h = srs.get(q["id"], {}).get("history", [])
        return bool(h) and not h[-1]["correct"]

    if mode == "new":
        qs = [q for q in qs if q["id"] not in srs]
    elif mode == "wrong":
        qs = [q for q in qs if last_wrong(q) or srs.get(q["id"], {}).get("lapses", 0) > 0]
        qs.sort(key=lambda q: (-srs[q["id"]].get("lapses", 0), srs[q["id"]]["due"]))
    elif mode == "random":
        random.shuffle(qs)
    elif mode == "due":
        due = sorted((q for q in qs if q["id"] in srs and srs[q["id"]]["due"] <= today),
                     key=lambda q: (srs[q["id"]]["due"], srs[q["id"]]["ef"]))
        new = [q for q in qs if q["id"] not in srs]
        rest = sorted((q for q in qs if q["id"] in srs and srs[q["id"]]["due"] > today),
                      key=lambda q: srs[q["id"]]["due"])
        qs = due + new + rest
    elif mode != "all":
        raise StudyError(f"알 수 없는 mode: {mode}")
    return qs[:limit] if limit else qs


def compute_stats(slug: str) -> dict:
    bank = load_bank(slug)
    by_id = {q["id"]: q for q in bank["questions"]}
    srs = load_srs(slug)
    attempts = load_attempts(slug)
    today = date.today()
    week = (today + timedelta(days=7)).isoformat()

    responses = [r for a in attempts for r in a["responses"] if r["qid"] in by_id]
    matrix = {c: {"correct": 0, "wrong": 0} for c in CONFIDENCES}
    by_concept = defaultdict(lambda: {"n": 0, "correct": 0, "sure_wrong": 0})
    by_domain = defaultdict(lambda: {"n": 0, "correct": 0})
    wrong_choices = defaultdict(lambda: defaultdict(int))
    for r in responses:
        q = by_id[r["qid"]]
        matrix[r["confidence"]]["correct" if r["correct"] else "wrong"] += 1
        for c in q.get("concepts") or ["(태그 없음)"]:
            by_concept[c]["n"] += 1
            by_concept[c]["correct"] += r["correct"]
            by_concept[c]["sure_wrong"] += (not r["correct"] and r["confidence"] == "sure")
        d = q.get("domain") or "(영역 없음)"
        by_domain[d]["n"] += 1
        by_domain[d]["correct"] += r["correct"]
        if not r["correct"]:
            wrong_choices[r["qid"]]["".join(r["selected"]) or (r.get("text") or "")] += 1

    def rate(d):
        return round(d["correct"] / d["n"], 3) if d["n"] else None

    concepts = {c: {**v, "accuracy": rate(v)} for c, v in by_concept.items()}
    weak = sorted(
        (c for c, v in concepts.items() if v["n"] >= 2 and (v["accuracy"] < 0.6 or v["sure_wrong"])),
        key=lambda c: (concepts[c]["accuracy"], -concepts[c]["sure_wrong"]),
    )
    last = {qid: s["history"][-1] for qid, s in srs.items() if s.get("history") and qid in by_id}
    sessions = [
        {"session": a["session"], "mode": a.get("mode"), "source": a.get("source"),
         "n": len(a["responses"]), "correct": sum(r["correct"] for r in a["responses"])}
        for a in attempts
    ]
    return {
        "topic": slug,
        "title": bank.get("title", slug),
        "questions": len(by_id),
        "attempted": len([q for q in srs if q in by_id]),
        "responses": len(responses),
        "accuracy": rate({"n": len(responses), "correct": sum(r["correct"] for r in responses)}),
        "sessions": sessions,
        "confidence_matrix": matrix,
        "by_domain": {d: {**v, "accuracy": rate(v)} for d, v in sorted(by_domain.items())},
        "by_concept": dict(sorted(concepts.items(), key=lambda kv: (kv[1]["accuracy"] or 0, kv[0]))),
        "weak_concepts": weak,
        "currently_wrong": sorted(q for q, h in last.items() if not h["correct"]),
        "sure_wrong": sorted(q for q, h in last.items() if not h["correct"] and h["confidence"] == "sure"),
        "guess_correct": sorted(q for q, h in last.items() if h["correct"] and h["confidence"] != "sure"),
        "repeat_wrong": sorted(q for q, s in srs.items() if s.get("lapses", 0) >= 2 and q in by_id),
        "repeated_wrong_choice": {q: dict(c) for q, c in wrong_choices.items() if max(c.values()) >= 2},
        "missing_explanation": sorted(q for q, v in by_id.items() if not str(v.get("explanation", "")).strip()),
        "due_today": len([q for q, s in srs.items() if q in by_id and s["due"] <= today.isoformat()]),
        "due_week": len([q for q, s in srs.items() if q in by_id and s["due"] <= week]),
        "srs": {q: {k: s[k] for k in ("due", "interval", "lapses", "ef")} | {
            "history": [f"{'✓' if h['correct'] else '✗'} {h['date'][5:]}" for h in s["history"]]}
            for q, s in srs.items() if q in by_id},
    }


def print_stats(st: dict) -> None:
    pct = lambda v: "-" if v is None else f"{v * 100:.0f}%"
    print(f"# {st['title']} ({st['topic']})")
    print(f"문항 {st['questions']} · 푼 문항 {st['attempted']} · 응답 {st['responses']} · 정답률 {pct(st['accuracy'])}")
    print(f"복습: 오늘 {st['due_today']} · 7일 내 {st['due_week']}")
    if not st["responses"]:
        print("아직 풀이 기록이 없습니다.")
        return
    m = st["confidence_matrix"]
    print("\n확신도   맞음  틀림")
    for c, label in zip(CONFIDENCES, ("확실", "애매", "찍음")):
        print(f"  {label}   {m[c]['correct']:4} {m[c]['wrong']:5}")
    print("\n영역별")
    for d, v in st["by_domain"].items():
        print(f"  {d}: {v['correct']}/{v['n']} ({pct(v['accuracy'])})")
    print("\n약한 개념:", ", ".join(st["weak_concepts"]) or "-")
    print("현재 오답:", ", ".join(st["currently_wrong"]) or "-")
    print("확신 오답:", ", ".join(st["sure_wrong"]) or "-")
    print("찍어서/애매하게 맞힘:", ", ".join(st["guess_correct"]) or "-")
    print("반복 오답(2회+):", ", ".join(st["repeat_wrong"]) or "-")
    if st["missing_explanation"]:
        print(f"해설 없는 문항: {len(st['missing_explanation'])}개")


# ---------------------------------------------------------------- 주제 생성·문항 추가

DOC_TEMPLATES = {
    "index.md": "# {title}\n\n{title} 학습 노트입니다.\n\n"
                "| 노트 | 내용 |\n|------|------|\n"
                "| [기본 개념](concepts.md) | 핵심 개념 요약 |\n"
                "| [헷갈리는 개념](confusions.md) | 비교표와 판별 규칙 |\n"
                "| [오답노트](wrong-notes.md) | 틀린 문제와 교훈 |\n\n"
                "## 학습 현황\n\n아직 풀이 기록이 없습니다.\n",
    "concepts.md": "# 기본 개념\n\n!!! note \"작성 중\"\n    개념 노트를 준비하고 있습니다.\n",
    "confusions.md": "# 헷갈리는 개념\n\n!!! note \"작성 중\"\n    비교 노트를 준비하고 있습니다.\n",
    "wrong-notes.md": "# 오답노트\n\n!!! note \"아직 없음\"\n    문제를 풀고 나면 오답이 여기에 정리됩니다.\n",
}


def refresh_home() -> None:
    """docs/index.md 의 주제 목록을 docs/topics/*/index.md 제목으로 다시 쓴다."""
    home = ROOT / "docs" / "index.md"
    start, end = "<!-- topics:start -->", "<!-- topics:end -->"
    items = []
    for d in sorted(DOCS.iterdir()) if DOCS.exists() else []:
        idx = d / "index.md"
        if idx.exists():
            first = idx.read_text(encoding="utf-8").splitlines()[0]
            items.append(f"- [{first.lstrip('# ').strip()}](topics/{d.name}/index.md)")
    block = "\n".join([start, *(items or ["아직 주제가 없습니다."]), end])
    text = home.read_text(encoding="utf-8") if home.exists() else f"# 학습 노트\n\n## 주제\n\n{start}\n{end}\n"
    if start not in text:
        text += f"\n## 주제\n\n{start}\n{end}\n"
    text = re.sub(re.escape(start) + r".*?" + re.escape(end), lambda _: block, text, flags=re.S)
    home.write_text(text, encoding="utf-8")


def cmd_new_topic(slug: str, title: str) -> None:
    tdir = topic_dir(slug)
    (tdir / "attempts").mkdir(parents=True, exist_ok=True)
    if not (tdir / "questions.json").exists():
        write_json(tdir / "questions.json", {"topic": slug, "title": title, "questions": []})
    ddir = DOCS / slug
    ddir.mkdir(parents=True, exist_ok=True)
    created = []
    for name, tmpl in DOC_TEMPLATES.items():
        if not (ddir / name).exists():
            (ddir / name).write_text(tmpl.format(title=title), encoding="utf-8")
            created.append(name)
    refresh_home()
    print(f"주제 준비됨: {slug}")
    print(f"  비공개: {tdir.relative_to(ROOT)}/")
    print(f"  공개:   {ddir.relative_to(ROOT)}/ (새로 만든 파일: {', '.join(created) or '없음'})")


def next_id_num(bank: dict) -> int:
    nums = [int(q["id"][1:]) for q in bank["questions"] if re.match(r"^q\d+$", q.get("id", ""))]
    return max(nums, default=0) + 1


def stem_key(stem: str) -> str:
    return normalize_text(re.sub(r"[^\w\s]", "", stem))[:300]


def merge_questions(slug: str, new: list[dict], default_source: str = "generated") -> tuple[int, int]:
    bank = load_bank(slug)
    existing = {stem_key(q["stem"]) for q in bank["questions"]}
    num = next_id_num(bank)
    added, skipped, staged, errors = 0, 0, [], []
    concept_ids = concept_ids_from_research(slug)
    for q in new:
        key = stem_key(q.get("stem", ""))
        if key in existing:
            skipped += 1
            continue
        q = {"id": f"q{num:03d}", **{k: v for k, v in q.items() if k != "id"}}
        q.setdefault("explanation", "")
        q.setdefault("concepts", [])
        q.setdefault("source", default_source)
        e, _ = validate_question(q, concept_ids)
        if e:
            errors += e
            continue
        staged.append(q)
        existing.add(key)
        num += 1
        added += 1
    if errors:
        raise StudyError("검증 실패 — 아무것도 저장하지 않았습니다:\n  " + "\n  ".join(errors))
    bank["questions"] += staged
    save_bank(slug, bank)
    return added, skipped


# ---------------------------------------------------------------- 기출 마크다운 가져오기

Q_HEAD = re.compile(r"^#*\s*\**\s*QUESTION\s+(\d+)\s*\**\s*$", re.I)
CHOICE = re.compile(r"^\s*[-*]?\s*\**([A-H])[.)]\**\s+(.*\S)\s*$")
ANSWER = re.compile(r"^#*\s*\**\s*Correct Answer:?\s*\**:?\s*([A-H](?:\s*,?\s*[A-H])*)\s*$", re.I)
EXPL = re.compile(r"^#*\s*\**\s*Explanation(?:/Reference)?:?\s*\**:?\s*$", re.I)
URL = re.compile(r"https?://\S+")


def clean_md(s: str) -> str:
    s = re.sub(r"</?u>", "", s)
    s = s.replace("**", "")
    return re.sub(r"[ \t]+", " ", s).strip()


def parse_exam_md(text: str, source_name: str) -> list[dict]:
    """'QUESTION N' / '- A. ...' / 'Correct Answer: X' 형식 문서를 문항 목록으로 바꾼다."""
    blocks, cur = [], None
    for line in text.splitlines():
        m = Q_HEAD.match(line.strip())
        if m:
            cur = {"num": int(m.group(1)), "lines": []}
            blocks.append(cur)
        elif cur is not None:
            cur["lines"].append(line)

    out = []
    for b in blocks:
        stem, choices, answer, expl, refs = [], {}, None, [], []
        state = "stem"
        last_choice = None
        for raw in b["lines"]:
            line = raw.strip()
            if not line:
                continue
            if (m := ANSWER.match(line)):
                answer = re.findall(r"[A-H]", m.group(1).upper())
                state = "after"
                continue
            if EXPL.match(line) or clean_md(line.lstrip("# ")).lower() in ("explanation", "ref"):
                state = "expl"
                continue
            if state in ("stem", "choices") and (m := CHOICE.match(line)):
                choices[m.group(1)] = clean_md(m.group(2))
                last_choice = m.group(1)
                state = "choices"
                continue
            if state == "stem":
                stem.append(clean_md(line.lstrip("# ")))
            elif state == "choices" and last_choice:  # 선택지가 여러 줄로 이어지는 경우
                choices[last_choice] += " " + clean_md(line)
            elif state == "expl":
                refs += URL.findall(line)
                rest = URL.sub("", clean_md(line.lstrip("# "))).strip()
                if rest:
                    expl.append(rest)
        if not stem or len(choices) < 2 or not answer:
            print(f"  건너뜀: {source_name} QUESTION {b['num']} (본문/선택지/정답 인식 실패)", file=sys.stderr)
            continue
        q = {
            "type": "multi" if len(answer) > 1 else "single",
            "stem": "\n\n".join(stem),
            "choices": choices,
            "answer": answer,
            "explanation": "\n".join(expl),
            "concepts": [],
            "source": f"import:{source_name}#{b['num']}",
        }
        if refs:
            q["refs"] = refs
        out.append(q)
    return out


def cmd_import_md(slug: str, files: list[str]) -> None:
    total_added = total_skipped = 0
    for f in files:
        path = Path(f)
        qs = parse_exam_md(path.read_text(encoding="utf-8"), path.name)
        added, skipped = merge_questions(slug, qs, default_source=f"import:{path.name}")
        print(f"{path.name}: 인식 {len(qs)} · 추가 {added} · 중복 건너뜀 {skipped}")
        total_added += added
        total_skipped += skipped
    print(f"합계: 추가 {total_added} · 중복 {total_skipped}")


# ---------------------------------------------------------------- 웹 서버

class Handler(BaseHTTPRequestHandler):
    server_version = "StudyQuiz/1.0"

    def log_message(self, fmt, *args):  # 조용히
        pass

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def route(self):
        url = urlparse(self.path)
        parts = [p for p in url.path.split("/") if p]
        qs = {k: v[0] for k, v in parse_qs(url.query).items()}
        return parts, qs

    def do_GET(self):
        parts, qs = self.route()
        try:
            if not parts:
                body = QUIZ_HTML.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif parts == ["api", "topics"]:
                out = []
                for slug in list_topics():
                    st = compute_stats(slug)
                    out.append({k: st[k] for k in ("topic", "title", "questions", "attempted", "accuracy", "due_today")}
                               | {"new": st["questions"] - st["attempted"], "wrong": len(st["currently_wrong"]),
                                  "concepts": sorted({c for q in load_bank(slug)["questions"] for c in q.get("concepts", [])})})
                self.send_json(out)
            elif len(parts) == 4 and parts[:2] == ["api", "topics"] and parts[3] == "session":
                limit = int(qs.get("limit", 20))
                picked = pick_questions(parts[2], qs.get("mode", "due"), limit, qs.get("concept") or None)
                self.send_json({"session": new_session_id(), "questions": [public_question(q) for q in picked]})
            elif len(parts) == 4 and parts[:2] == ["api", "topics"] and parts[3] == "stats":
                self.send_json(compute_stats(parts[2]))
            else:
                self.send_json({"error": "not found"}, 404)
        except StudyError as e:
            self.send_json({"error": str(e)}, 400)

    def do_POST(self):
        parts, _ = self.route()
        try:
            length = int(self.headers.get("Content-Length") or 0)
            data = json.loads(self.rfile.read(length) or b"{}")
            if len(parts) == 4 and parts[:2] == ["api", "topics"] and parts[3] == "answer":
                result = record_response(parts[2], data.get("session", ""), data,
                                         mode=data.get("mode", "due"), source="web")
                self.send_json(result)
            else:
                self.send_json({"error": "not found"}, 404)
        except (StudyError, json.JSONDecodeError) as e:
            self.send_json({"error": str(e)}, 400)


def cmd_serve(port: int) -> None:
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"로컬 퀴즈: http://localhost:{port}  (Ctrl+C로 종료)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


# ---------------------------------------------------------------- main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="study.py", description="학습 서비스 CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("new-topic"); p.add_argument("slug"); p.add_argument("--title", required=True)
    p = sub.add_parser("import-md"); p.add_argument("slug"); p.add_argument("files", nargs="+")
    p = sub.add_parser("add-questions"); p.add_argument("slug"); p.add_argument("file")
    p = sub.add_parser("validate"); p.add_argument("slug")
    p = sub.add_parser("serve"); p.add_argument("--port", type=int, default=8765)
    p = sub.add_parser("due"); p.add_argument("slug"); p.add_argument("--limit", type=int, default=10)
    p.add_argument("--mode", default="due"); p.add_argument("--concept"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("record"); p.add_argument("slug"); p.add_argument("file")
    p = sub.add_parser("stats"); p.add_argument("slug"); p.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    try:
        if a.cmd == "new-topic":
            cmd_new_topic(a.slug, a.title)
        elif a.cmd == "import-md":
            cmd_import_md(a.slug, a.files)
        elif a.cmd == "add-questions":
            data = read_json(Path(a.file), None)
            new = data["questions"] if isinstance(data, dict) else data
            added, skipped = merge_questions(a.slug, new)
            print(f"추가 {added} · 중복 건너뜀 {skipped}")
        elif a.cmd == "validate":
            errors, warnings = validate_bank(a.slug, load_bank(a.slug))
            for w in warnings[:50]:
                print("경고:", w)
            if len(warnings) > 50:
                print(f"경고 {len(warnings) - 50}개 더 있음")
            for e in errors:
                print("오류:", e)
            print(f"오류 {len(errors)} · 경고 {len(warnings)}")
            return 1 if errors else 0
        elif a.cmd == "serve":
            cmd_serve(a.port)
        elif a.cmd == "due":
            picked = pick_questions(a.slug, a.mode, a.limit, a.concept)
            srs = load_srs(a.slug)
            if a.json:
                print(json.dumps(picked, ensure_ascii=False, indent=1))
            else:
                for q in picked:
                    s = srs.get(q["id"])
                    tag = f"복습 {s['due']}" if s else "새 문항"
                    print(f"{q['id']} [{tag}] {q['stem'][:70]}")
        elif a.cmd == "record":
            data = read_json(Path(a.file), None)
            sid = new_session_id("chat")
            bank = load_bank(a.slug)
            results = [record_response(a.slug, sid, r, mode=data.get("mode", "chat"), source="chat", bank=bank)
                       for r in data["responses"]]
            n_ok = sum(r["correct"] for r in results)
            print(f"기록됨: {sid} · {n_ok}/{len(results)} 정답")
            for r, res in zip(data["responses"], results):
                print(f"  {r['qid']}: {'✓' if res['correct'] else '✗ 정답 ' + ','.join(res['answer'])} · 다음 복습 {res['next_due']}")
        elif a.cmd == "stats":
            st = compute_stats(a.slug)
            print(json.dumps(st, ensure_ascii=False, indent=1)) if a.json else print_stats(st)
    except StudyError as e:
        print(f"오류: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
