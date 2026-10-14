#!/usr/bin/env bash
# StopFailure 훅 (matcher: rate_limit)
# 한도 소진으로 턴이 끊긴 순간, 큰 작업 중이면 커밋 안 된 변경을 WIP 커밋으로 보존한다.
# Claude가 끊겨서 직접 커밋하지 못한 마지막 단계를 지키는 안전장치다.
. "$(dirname "$0")/lib-quota.sh"
cat >/dev/null

cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0
git rev-parse --git-dir >/dev/null 2>&1 || exit 0
heavy_task_active || exit 0
[ -n "$(git status --porcelain)" ] || exit 0

# notes에 자동 기록 추가 (임시 파일에 쓴 뒤 교체해 JSON이 깨지지 않게 한다)
line="[auto] $(date '+%m/%d %H:%M') 한도 소진으로 중단. 직전 변경은 wip 커밋에 있음."
tmp="${PROGRESS_FILE}.tmp.$$"
if jq --arg l "$line" '.notes = ((.notes // []) + [$l])' "$PROGRESS_FILE" > "$tmp"; then
  mv "$tmp" "$PROGRESS_FILE"
else
  rm -f "$tmp"
fi

# --no-verify: pre-commit 훅(린트·테스트)이 미완성 코드에서 실패해 저장이 막히는 것을 피한다.
# git add -u: 이미 추적 중인 파일의 변경만 저장한다. 새 파일(.env, node_modules 등)이 의도치 않게 커밋되는 것을 막는다.
# 새 파일은 SKILL.md의 90% 절차(모델이 직접 커밋)에서 챙긴다.
git add -u && git commit -q --no-verify -m "wip: 한도 소진으로 중단 (자동 저장)"
exit 0
