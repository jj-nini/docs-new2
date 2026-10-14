#!/usr/bin/env bash
# UserPromptSubmit 훅
# 사용률이 70% 이상일 때만 현재 한도 상황을 지시와 함께 Claude에게 붙여준다.
# Claude는 이 정보를 보고 작업을 큰 작업 절차로 할지, 잘게 나눌지 판단한다.
. "$(dirname "$0")/lib-quota.sh"
cat >/dev/null

read_quota || exit 0
[ "$MAX" -ge 70 ] || exit 0

msg="현재 사용 한도: 5시간 창 ${FIVE}%"
[ -n "$FIVE_RESET_HM" ] && msg="${msg} (리셋 ${FIVE_RESET_HM})"
msg="${msg}, 주간 ${WEEK}%."

jq -n --arg m "$msg" '{hookSpecificOutput:{hookEventName:"UserPromptSubmit", additionalContext:$m}}'
