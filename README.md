# docs-new2

학습 주제(키워드·URL·자료)를 주면 Claude Code 에이전트 팀이 노트와 문제를 만들고, **문제는 로컬에서 풀고**, **기본 개념·헷갈리는 개념·오답노트는 GitHub Pages로 공개**하는 학습 서비스입니다.
구조는 [harness-100](https://github.com/revfactory/harness-100)의 `57-exam-prep`, `56-language-tutor`를 참고했습니다.

공개 노트: https://jj-nini.github.io/docs-new2/

## 흐름

```
/study <키워드 | URL | sources/파일.md>
   │
   ├─ topic-researcher ─ 개념 맵·혼동 후보 (local/)
   ├─ concept-writer ── 기본 개념 ─────────┐
   ├─ confusion-analyst 헷갈리는 개념 ──────┤ docs/ → GitHub Pages
   └─ examiner ──────── 문제 은행 (local/)  │
                                            │
python3 tools/study.py serve  ← 로컬에서 풀기 (확신도 기록, SM-2 복습)
   또는 "대화로 10문제 내줘"                │
                                            │
"오답노트 정리해줘"                         │
   ├─ error-analyst ─── 오답노트·학습 현황 ─┤
   └─ confusion-analyst 실제 혼동으로 갱신 ─┘
"발행해줘" → commit → git push → Actions가 Pages 배포
```

## 사용법

| 하고 싶은 것 | Claude Code에서 |
|-------------|----------------|
| 새 주제 시작 | `/study 쿠버네티스 네트워킹` · `/study https://...` · `/study sources/reference/samples_first.md` |
| 웹에서 풀기 | `python3 tools/study.py serve` → http://localhost:8765 (키보드: A–H 선택, 1 확실 / 2 애매 / 3 찍음, Enter 다음) |
| 대화로 풀기 | "aws-ans-c01 복습할 거 10문제 내줘" |
| 오답노트 갱신 | "오답노트 정리해줘" |
| 약점 추가 출제 | "약한 개념 위주로 15문제 더 내줘" |
| 공개 | "발행해줘" (push는 확인 후) |

`tools/study.py`는 표준 라이브러리만 씁니다. 명령 목록은 `python3 tools/study.py -h`.

## 무엇이 공개되나

| 경로 | 내용 | 공개 |
|------|------|------|
| `docs/` | 개념·헷갈리는 개념·오답노트 | ✓ |
| `local/` | 문제 은행, 풀이 기록, 복습 상태 | ✗ (`.gitignore`) |
| `sources/` | 원본 자료 (기출 덤프 등) | ✗ (`.gitignore`) |

`local/`은 git에 올라가지 않으므로 따로 백업하세요. 공개 노트에는 문제 원문을 옮기지 않고 요지만 씁니다.

## GitHub Pages 최초 설정 (한 번만)

1. 저장소 **Settings → Pages → Build and deployment → Source**를 **GitHub Actions**로 바꿉니다.
2. `main`에 push하면 `.github/workflows/pages.yml`이 `mkdocs build --strict` 후 배포합니다.
3. 무료 계정은 공개 저장소여야 Pages를 쓸 수 있습니다.

로컬 미리보기: `uv run mkdocs serve` → http://127.0.0.1:8000

## 구성

```
.claude/
├── agents/   topic-researcher · concept-writer · confusion-analyst · examiner · error-analyst
└── skills/   study(오케스트레이터) · question-bank · error-pattern-analyzer · spaced-repetition · notes-style
tools/study.py, tools/quiz/index.html   로컬 퀴즈 서버·CLI
docs/                                    공개 노트 (MkDocs Material)
```
