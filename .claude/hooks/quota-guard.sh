#!/usr/bin/env bash
# PostToolUse 훅
# 큰 작업이 진행 중이고 사용률이 90% 이상이면 Claude에게 알린다.
# 같은 세션에서는 10분에 한 번만 알린다(도구마다 반복하지 않도록).
. "$(dirname "$0")/lib-quota.sh"
input=$(cat)

heavy_task_active || exit 0
read_quota || exit 0
[ "$MAX" -ge 90 ] || exit 0

sid=$(printf '%s' "$input" | jq -r '.session_id // "unknown"')
sid=${sid//[^A-Za-z0-9_-]/_}
stamp="${TMPDIR:-/tmp}/claude-quota-warned-${sid}"
if [ -f "$stamp" ]; then
  last=$(stat -c %Y "$stamp" 2>/dev/null || stat -f %m "$stamp")
  [ $(( $(date +%s) - last )) -lt 600 ] && exit 0
fi
touch "$stamp"

msg="사용 한도 ${MAX}% 도달 (5시간 창 ${FIVE}%, 주간 ${WEEK}%). heavy-task 절차의 90% 기준에 해당함."
jq -n --arg m "$msg" '{hookSpecificOutput:{hookEventName:"PostToolUse", additionalContext:$m}}'
