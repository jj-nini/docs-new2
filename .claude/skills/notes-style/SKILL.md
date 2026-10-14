---
name: notes-style
description: "GitHub Pages(MkDocs Material)로 공개되는 학습 노트의 작성 규칙: 파일 위치, 앵커, 링크, admonition 문법, 공개 금지 내용. concept-writer, confusion-analyst, error-analyst가 docs/ 아래 노트를 쓸 때 반드시 읽는다."
---

# Notes Style — 공개 노트 작성 규칙

## 파일과 역할

```
docs/
├── index.md                       ← 전체 홈 (주제 목록: new-topic이 관리)
└── topics/<slug>/
    ├── index.md                   ← 주제 홈: 소개·학습 현황·바로가기
    ├── concepts.md                ← 기본 개념
    ├── confusions.md              ← 헷갈리는 개념
    └── wrong-notes.md             ← 오답노트
```

각 파일은 front matter 없이 `# 제목`으로 시작한다. 파일 이름을 바꾸지 않는다.

## 앵커와 링크

- 개념: `### 이름 {#concept-id}` — ID는 `01_research.md` 개념 맵과 같아야 한다.
- 혼동 그룹: `## A vs B {#a-vs-b}` / 오답 문항: `### q012 · 요지 {#q012}`
- 링크는 같은 폴더 상대 경로: `[NAT 게이트웨이](concepts.md#nat-gateway)`
- 없는 앵커로 링크하면 `mkdocs build --strict`가 실패한다. 링크 전에 앵커가 있는지 grep으로 확인한다.

## 쓸 수 있는 문법 (mkdocs.yml에 켜져 있음)

```markdown
!!! note "제목"          ← 정보
!!! tip "기억법"          ← 암기 요령
!!! warning "헷갈리는 이유" ← 함정
??? question "셀프 체크"   ← 접힌 블록 (클릭해 펼침), 정답 숨기기에 사용

=== "게이트웨이"           ← 탭
    내용
=== "인터페이스"
    내용

| 표 | 지원 |
```

- 다이어그램이 꼭 필요하면 ```` ```mermaid ```` 코드 블록을 쓴다.
- 강조는 **굵게**만. 이모지는 심각도(🔴🟡🟢) 표시에만 쓴다.

## 공개 금지

- 문제 은행·기출 문항의 **원문**(본문, 선택지 전체). 요지를 한두 줄로 재서술한다.
- `local/`, `sources/`의 파일 경로나 개인 정보.
- 확인하지 않은 수치. 불확실하면 `(확인 필요)`.

## 문체

- 한국어 평서문(~다). 서비스명·기술 용어는 원어를 병기한다: "NAT 게이트웨이(NAT Gateway)" — 첫 등장 때만.
- 문단은 3줄 이내. 불릿과 표를 우선한다.
