#!/usr/bin/env bash
# SessionStart 훅
# 중단된 큰 작업(progress.json에 "doing" 단계)이 있을 때만 그 사실을 Claude에게 알린다.
# 없으면 아무것도 출력하지 않으므로 평소에는 컨텍스트를 쓰지 않는다.
. "$(dirname "$0")/lib-quota.sh"
cat >/dev/null   # stdin 입력은 사용하지 않음

heavy_task_active || exit 0

msg=$(jq -r '
  "중단된 큰 작업이 있음 (heavy-task 재개 대상). 작업: \(.task // "?"). " +
  "진행 중 단계: " + ([.steps[] | select(.status == "doing") | "\(.id). \(.title)"] | first // "?") + "." +
  (if ((.notes // []) | length) > 0
     then "\n최근 메모:\n" + ((.notes[-3:]) | map("- " + .) | join("\n"))
     else "" end)
' "$PROGRESS_FILE")

jq -n --arg m "$msg" '{hookSpecificOutput:{hookEventName:"SessionStart", additionalContext:$m}}'
