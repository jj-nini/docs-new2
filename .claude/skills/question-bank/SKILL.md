---
name: question-bank
description: "로컬 문제 은행(questions.json)의 스키마, 문항 품질 규칙, Bloom 인지 수준 분포, 오답 선택지 설계법. examiner 에이전트가 문항을 출제하거나 해설을 채울 때 사용한다. '문제 출제', '문항 형식', 'questions.json', '해설 작성', '선택지 설계' 맥락에서 적용한다."
---

# Question Bank — 문제 은행 형식과 출제 규칙

## 파일: `local/topics/<slug>/questions.json`

```json
{
  "topic": "aws-ans-c01",
  "title": "AWS Advanced Networking Specialty",
  "questions": [
    {
      "id": "q001",
      "type": "multi",
      "stem": "문제 본문 (마크다운 가능)",
      "choices": {"A": "...", "B": "...", "C": "...", "D": "...", "E": "..."},
      "answer": ["B", "E"],
      "explanation": "정답 근거",
      "why_wrong": {"A": "NLB는 L4라 경로 기반 라우팅 불가", "C": "...", "D": "..."},
      "concepts": ["alb", "x-forwarded-for"],
      "domain": "네트워크 설계",
      "difficulty": 2,
      "bloom": "apply",
      "source": "generated"
    }
  ]
}
```

| 필드 | 필수 | 규칙 |
|------|------|------|
| `id` | ✓ | `q` + 3자리 이상 숫자. `add-questions`가 자동 부여하므로 새 문항에는 생략해도 된다. **기존 id는 절대 바꾸지 않는다** (풀이 기록이 id로 연결됨) |
| `type` | ✓ | `single` (정답 1개) / `multi` (정답 2개 이상, 개수만큼 고름) / `short` (주관식) |
| `stem` | ✓ | 문제 본문. multi면 "(2개 고르시오)"처럼 고를 개수를 본문에 쓴다 |
| `choices` | single/multi | 키는 A, B, C… 연속 대문자 |
| `answer` | ✓ | single/multi: 선택지 키 배열. short: 허용 답안 문자열 배열 (대소문자·공백 무시하고 비교) |
| `explanation` | ✓ (빈 문자열 허용) | 정답 근거. 비어 있으면 C 모드에서 채운다 |
| `why_wrong` | 권장 | 오답 선택지별 틀린 이유 |
| `concepts` | ✓ | `01_research.md` 개념 맵의 ID. 1~3개 |
| `domain` | 권장 | 개념 맵의 영역 이름 |
| `difficulty` | 권장 | 1 쉬움 / 2 보통 / 3 어려움 |
| `bloom` | 권장 | remember / understand / apply / analyze / evaluate / create |
| `source` | ✓ | `generated` 또는 `import:<파일명>#<원래 번호>` |
| `flag` | 선택 | 정답 검토가 필요할 때 이유를 적는다 |

## 기본 출제 분포

| 축 | 분포 |
|----|------|
| 난이도 | 쉬움 30% / 보통 50% / 어려움 20% |
| Bloom | remember+understand 30% / apply 40% / analyze+evaluate 30% |
| 영역 | 리서치의 영역 가중치를 따른다 |
| 형식 | single 70% / multi 20% / short 10% (시험 형식이 정해져 있으면 그것을 따른다) |

## 품질 체크리스트 (문항마다)

- [ ] 정답이 하나로 확정되는가? (multi는 정확히 `answer` 개수만큼)
- [ ] 본문만 읽고 무엇을 묻는지 알 수 있는가? 이중 부정이 없는가?
- [ ] 정답이 길이·표현으로 티 나지 않는가? (가장 긴 선택지 = 정답 패턴 금지)
- [ ] 오답이 **실제 오해**에서 나왔는가? 터무니없는 선택지는 없는가?
- [ ] "모두 정답/모두 오답" 선택지를 쓰지 않았는가?
- [ ] 해설이 정답 근거와 각 오답의 틀린 이유를 모두 다루는가?

## 오답 선택지 설계

1. **혼동 쌍 활용**: 리서치의 혼동 후보에서 짝 개념을 오답으로 넣는다 (게이트웨이 ↔ 인터페이스 엔드포인트).
2. **조건 일부만 충족**: 요구사항 3개 중 2개만 만족하는 선택지 (비용은 맞는데 고가용성 불충족).
3. **과거엔 맞았던 사실**: 기능 변경 전 동작 (확인된 경우만).
4. **용어 바꿔치기**: 존재하지 않거나 다른 서비스의 기능 이름.

## Bloom 수준별 문항 틀

| 수준 | 묻는 방식 |
|------|----------|
| remember | "X의 기본값/한도는?" |
| understand | "X가 Y와 다른 이유는?" |
| apply | "요구사항이 이러할 때 어떤 구성을?" (시나리오) |
| analyze | "이 증상의 원인은?" (트러블슈팅) |
| evaluate | "가장 비용 효율적인/운영 부담이 적은 방법은?" |
