---
name: study
description: "학습 서비스 오케스트레이터. 학습 주제(키워드·URL·로컬 파일)를 받아 주제 분석→기본 개념 노트→헷갈리는 개념→문제 은행을 만들고, 로컬 웹 퀴즈나 대화로 문제를 풀게 한 뒤, 풀이 기록으로 오답노트를 갱신해 GitHub Pages에 공개한다. '/study', '공부하자', '학습 주제', '문제 내줘', '퀴즈', '오답노트', '헷갈리는 개념 정리', '복습할 것', '노트 발행' 등에 사용한다. 실제 시험 접수나 유료 강의 추천은 범위가 아니다."
---

# Study — 학습 서비스 오케스트레이터

`harness-100/57-exam-prep`, `56-language-tutor`의 에이전트 팀 구조를 따르되, **문제는 로컬에서 풀고 노트만 공개**하도록 나눈다.

## 공개/비공개 경계 (항상 지킨다)

| 위치 | 내용 | 공개 |
|------|------|------|
| `local/topics/<slug>/` | 입력, 리서치, `questions.json`, `attempts/`, `srs.json` | ✗ (gitignore) |
| `sources/` | 사용자가 넣은 원본 자료 (기출 덤프 등) | ✗ (gitignore) |
| `docs/topics/<slug>/` | `index.md`, `concepts.md`, `confusions.md`, `wrong-notes.md` | ✓ GitHub Pages |

`docs/`에 문제 원문(특히 기출)을 그대로 옮기지 않는다. 요지 재서술만 허용한다.

## 에이전트 구성

| 에이전트 | 파일 | 산출물 |
|---------|------|-------|
| topic-researcher | `.claude/agents/topic-researcher.md` | `local/topics/<slug>/01_research.md` |
| concept-writer | `.claude/agents/concept-writer.md` | `docs/topics/<slug>/concepts.md` |
| confusion-analyst | `.claude/agents/confusion-analyst.md` | `docs/topics/<slug>/confusions.md` |
| examiner | `.claude/agents/examiner.md` | `local/topics/<slug>/questions.json` |
| error-analyst | `.claude/agents/error-analyst.md` | `docs/topics/<slug>/wrong-notes.md`, `index.md`의 학습 현황 |

호출: Agent 도구의 `subagent_type`에 에이전트 이름을 쓴다. 이 세션에서 아직 등록되지 않았다면 `general-purpose`로 호출하고 프롬프트 첫 줄에 "`.claude/agents/<이름>.md`를 읽고 그 역할로 작업하라"를 넣는다. 모든 프롬프트에 `slug`, 관련 파일 경로, 이번 작업 범위를 명시한다.

## 도구: `tools/study.py` (표준 라이브러리만 사용)

| 명령 | 용도 |
|------|------|
| `python3 tools/study.py new-topic <slug> --title "<제목>"` | local/docs 디렉토리와 노트 골격 생성, 홈 목록에 추가 |
| `python3 tools/study.py import-md <slug> <파일.md> [...]` | `QUESTION N / - A. / Correct Answer:` 형식 기출 가져오기 (중복 제거) |
| `python3 tools/study.py add-questions <slug> <new.json>` | 새 문항 검사·id 부여·병합 |
| `python3 tools/study.py validate <slug>` | 문제 은행 스키마 검사 |
| `python3 tools/study.py serve [--port 8765]` | 로컬 웹 퀴즈 (http://localhost:8765) |
| `python3 tools/study.py due <slug> [--limit N] [--json]` | 오늘 복습할 문항 (SRS) |
| `python3 tools/study.py record <slug> <responses.json>` | 대화형 풀이 결과 채점·저장·SRS 갱신 |
| `python3 tools/study.py stats <slug> [--json]` | 정답률·개념별·확신도 매트릭스·반복 오답 |

## 모드 판별

| 사용자 요청 | 모드 |
|------------|------|
| 새 키워드/URL/파일 + "공부/학습/정리" | **A. 새 주제** |
| "문제 풀래", "퀴즈", "복습할 거" | **B. 풀이** (웹 or 대화형) |
| "다 풀었어", "오답노트 정리", "채점 결과 분석" | **C. 오답 분석** |
| "문제 더 내줘", "약점 위주로 출제" | **D. 추가 출제** |
| "개념 보강", "이 부분 더 설명" | **E. 노트 보강** |
| "발행", "올려줘", "배포" | **F. 발행** |

주제가 여러 개면 `ls local/topics`로 확인하고, 모호하면 어떤 주제인지 묻는다.

---

## A. 새 주제

### A-1. 준비 (직접 수행)
1. 입력에서 추출: **주제**, **소스 종류**(키워드/URL/로컬 파일), **목표**(시험명·합격선 등, 선택), **현재 수준**(선택), **문항 수**(기본 20).
2. slug를 정한다 (ASCII kebab-case, 예: `aws-ans-c01`, `kubernetes-networking`). 이미 있으면 그 주제에 이어서 작업한다.
3. `python3 tools/study.py new-topic <slug> --title "<제목>"`
4. `local/topics/<slug>/00_input.md`에 입력을 정리해 쓴다 (소스 URL·파일 경로 포함).

### A-2. 팀 실행

| 순서 | 작업 | 담당 | 의존 |
|------|------|------|------|
| 1 | 주제 분석, 개념 맵 | topic-researcher | 없음 |
| 2a | 기본 개념 노트 | concept-writer | 1 |
| 2b | 헷갈리는 개념 노트 (풀이 기록 없이 후보 기반) | confusion-analyst | 1 |
| 2c | 문제 은행 | examiner 또는 import-md | 1 |

- 2a·2b·2c는 **한 메시지에서 병렬로** 호출한다.
- 소스가 `QUESTION N` 형식 기출 파일이면 2c는 `import-md`로 가져오고, examiner에게는 **개념 태깅 + 해설 채우기를 30문항씩** 맡긴다 (전체를 한 번에 맡기지 않는다. 나머지는 오답이 난 문항부터 C 모드에서 채운다).
- 그 외에는 examiner가 지정 문항 수만큼 출제한다.

### A-3. 마무리
1. `uv run mkdocs build --strict`로 링크·앵커 오류를 확인하고 고친다.
2. 사용자에게 보고: 개념 수, 혼동 그룹 수, 문항 수, 그리고 **다음 행동**:
   - 웹으로 풀기: `python3 tools/study.py serve` → http://localhost:8765
   - 여기서 풀기: "대화로 10문제 내줘"
   - 다 풀면: "오답노트 정리해줘"

## B. 풀이

**웹 (기본 권장)**: `python3 tools/study.py serve`를 Bash `run_in_background`로 띄우고 주소를 알려준다. 웹 UI가 채점·기록·SRS 갱신을 모두 한다. 사용자가 끝났다고 하면 C로 간다.

**대화형**:
1. `python3 tools/study.py due <slug> --limit 10 --json`으로 문항을 고른다 (복습 예정 → 오답 → 새 문항 순으로 이미 정렬됨). 사용자가 개념/영역을 지정하면 그에 맞게 `questions.json`에서 고른다.
2. 한 번에 한 문항씩 낸다. **정답을 미리 보여주지 않는다.**
   - 선택지 4개 이하: AskUserQuestion으로 [답(복수정답이면 multiSelect), 확신도(확실/애매/찍음)] 두 질문을 한 번에 묻는다.
   - 선택지 5개 이상 또는 주관식: 문항을 텍스트로 보여주고 "답 + 확신도"(예: `BE 애매`)로 답하게 한다.
3. 각 답 직후 정오와 짧은 해설(정답 근거 + 고른 오답이 틀린 이유)을 보여준다.
4. 끝나면 응답을 `local/topics/<slug>/_chat_responses.json`에 쓰고 `python3 tools/study.py record <slug> local/topics/<slug>/_chat_responses.json`으로 저장한다. 형식:

        {"responses": [{"qid": "q001", "selected": ["B","E"], "confidence": "unsure", "seconds": 0}]}
   주관식은 `"text": "<답>"`. 채점은 record가 한다.
5. 결과 요약을 보여주고 C를 제안한다.

## C. 오답 분석

1. `python3 tools/study.py stats <slug>`로 기록이 있는지 확인한다. 없으면 B로 안내.
2. 오답 문항 중 `explanation`이 빈 것이 있으면 **먼저** examiner에게 해당 id들의 해설 채우기를 맡긴다.
3. error-analyst 호출 → 오답노트·학습 현황 갱신. 보고에서 (a) 혼동 증거, (b) 결손 개념을 받는다.
4. (a)가 있으면 confusion-analyst에게 넘겨 `confusions.md`를 갱신한다. 결손 개념이 개념 노트에서 빈약하면 concept-writer에게 해당 앵커 보강을 맡긴다 (둘은 병렬).
5. (b)가 3개 이상이면 "약점 개념으로 N문항 추가 출제할까요?"를 제안한다 (D).
6. `uv run mkdocs build --strict` 확인 후 F를 제안한다.

## D. 추가 출제
examiner에게 대상 개념/영역, 문항 수, 난이도를 넘긴다. 약점 기반이면 `stats --json`의 `weak_concepts`를 함께 넘긴다.

## E. 노트 보강
concept-writer 또는 confusion-analyst를 범위를 좁혀 호출한다. 앵커 ID는 바꾸지 않는다.

## F. 발행
1. `uv run mkdocs build --strict` 통과를 확인한다.
2. `git status --short`로 바뀐 파일이 `docs/`와 설정 파일뿐인지 확인한다. `local/`·`sources/`가 보이면 중단하고 .gitignore를 고친다.
3. `git add docs mkdocs.yml && git commit -m "notes(<slug>): <요약>"`
4. push는 사용자가 원할 때만 한다: `git push origin main`. push 후 GitHub Actions가 Pages로 배포한다 (`https://<user>.github.io/<repo>/`).

## 에러 핸들링

| 상황 | 대응 |
|------|------|
| 주제 미지정 ("공부하자"만) | 주제(키워드/URL/파일)를 묻는다 |
| 웹 검색·URL 실패 | 일반 지식으로 진행하고 리서치에 "데이터 제한" 명시 |
| 에이전트 실패 | 1회 재시도 → 실패하면 해당 산출물 없이 진행하고 보고 |
| `mkdocs build --strict` 실패 | 깨진 링크/앵커를 고친다. 앵커가 없으면 링크를 개념 노트 최상단으로 바꾼다 |
| 풀이 기록 없음 | 오답 분석 대신 풀이를 안내 |
