#!/usr/bin/env bash
# 공용 함수: ~/.claude/quota.json(상태줄 스크립트가 기록)을 읽어 변수로 만든다.
#   FIVE, WEEK      : 사용률(정수 %). 리셋 시각이 이미 지난 창은 0으로 본다.
#   FIVE_RESET_HM   : 5시간 창 리셋 시각 (HH:MM, 모르면 빈 값)
#   MAX             : FIVE와 WEEK 중 큰 값
# quota.json이 없으면 1을 반환한다.

read_quota() {
  local q="$HOME/.claude/quota.json" now r
  [ -f "$q" ] || return 1
  now=$(date +%s)
  read -r FIVE WEEK r < <(jq -r --argjson now "$now" '
    def pct($w): if (($w.resets_at // 0) > $now) then (($w.used_percentage // 0) | floor) else 0 end;
    [pct(.five_hour), pct(.seven_day), (.five_hour.resets_at // 0)] | @tsv' "$q" 2>/dev/null) || return 1
  FIVE=${FIVE:-0}; WEEK=${WEEK:-0}
  MAX=$(( FIVE > WEEK ? FIVE : WEEK ))
  FIVE_RESET_HM=""
  if [ "${r:-0}" -gt "$now" ]; then
    FIVE_RESET_HM=$(date -d "@$r" +%H:%M 2>/dev/null || date -r "$r" +%H:%M 2>/dev/null)
  fi
  return 0
}

# 진행 상태 파일 위치 (이름·위치를 바꾸려면 여기와 SKILL.md만 고치면 된다)
PROGRESS_FILE="$CLAUDE_PROJECT_DIR/progress.json"

# 큰 작업이 진행 중인지: progress.json에 status가 "doing"인 단계가 있으면 진행 중
# (파일이 없거나 JSON이 깨졌으면 진행 중이 아닌 것으로 본다)
heavy_task_active() {
  jq -e 'any(.steps[]?; .status == "doing")' "$PROGRESS_FILE" >/dev/null 2>&1
}
