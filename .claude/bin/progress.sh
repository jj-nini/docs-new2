#!/usr/bin/env bash
# progress.json 전용 CLI. Claude는 progress.json을 직접 읽거나 편집하지 않고 이 명령만 쓴다.
# 출력은 필요한 줄만 짧게 내보내므로 파일 전체가 컨텍스트에 들어가지 않는다.
#
#   progress.sh init "<작업명>" "<목표>" "<id>:<제목>" ...   새로 만들기 (첫 단계가 doing)
#   progress.sh status                                       한 줄 요약 + 진행 중 단계 + 최근 메모 3개
#   progress.sh steps                                        단계 목록 (id 상태 제목)
#   progress.sh done  <id>                                   완료 처리 후 다음 todo를 doing으로
#   progress.sh block <id> "<이유>"                          막힘 처리 후 다음 todo를 doing으로
#   progress.sh start <id>                                   지정 단계를 doing으로 (기존 doing은 todo로)
#   progress.sh add   <id> "<제목>" [<이 id 뒤에>]           단계 추가 (위치 생략 시 맨 뒤)
#   progress.sh note  "<내용>"                               메모 추가
#   progress.sh finish                                       파일 삭제 (작업 완료)
set -euo pipefail

# 스크립트 위치(<프로젝트>/.claude/bin) 기준으로 잡는다. git 루트가 프로젝트 폴더와 다른 경우와, 훅 밖(! 명령)에서 CLAUDE_PROJECT_DIR가 없는 경우를 모두 처리.
ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
F="$ROOT/progress.json"

die() { echo "progress: $*" >&2; exit 1; }
# 동시 세션/병렬 호출에서 갱신이 유실되지 않게 전체를 직렬화한다 (락 파일은 /tmp에 둬서 저장소를 더럽히지 않음).
# 내부에서 "$0" status를 다시 부를 때는 이미 락을 쥐고 있으므로 건너뛴다(PROGRESS_LOCKED).
if [ -z "${PROGRESS_LOCKED:-}" ]; then
  exec 9>"${TMPDIR:-/tmp}/claude-progress-$(printf '%s' "$F" | cksum | cut -d' ' -f1).lock"
  flock 9
  export PROGRESS_LOCKED=1
fi
need() { [ -f "$F" ] || die "progress.json 없음 (init 먼저)"; }

# jq 필터를 적용해 임시 파일에 쓰고, 유효할 때만 교체한다.
apply() {
  local tmp="$F.tmp.$$"
  if jq "$@" "$F" > "$tmp" && jq empty "$tmp"; then mv "$tmp" "$F"; else rm -f "$tmp"; die "갱신 실패"; fi
}

# 진행 중 단계가 없으면 첫 todo를 doing으로 올리는 필터
ADVANCE='if any(.steps[]; .status == "doing") then .
         else (first(.steps | to_entries[] | select(.value.status == "todo") | .key) // null) as $i
              | if $i == null then . else .steps[$i].status = "doing" end end'

has_id() { jq -e --arg id "$1" 'any(.steps[]; .id == $id)' "$F" >/dev/null || die "없는 단계 id: $1"; }

cmd="${1:-status}"; shift || true
case "$cmd" in
  init)
    [ -f "$F" ] && die "이미 있음. status로 확인하거나 finish 후 다시 init"
    [ $# -ge 3 ] || die '사용법: init "<작업명>" "<목표>" "<id>:<제목>" ...'
    task="$1"; goal="$2"; shift 2
    for s in "$@"; do
      [[ "$s" =~ ^[^:]+:.+$ ]] || die "단계 형식은 <id>:<제목> (잘못된 값: $s)"
    done
    [ -z "$(printf '%s\n' "$@" | cut -d: -f1 | sort | uniq -d)" ] || die "단계 id 중복"
    tmp="$F.tmp.$$"
    if printf '%s\n' "$@" | jq -R 'capture("^(?<id>[^:]+):(?<title>.*)$")' \
        | jq -s --arg t "$task" --arg g "$goal" \
            '{task:$t, goal:$g, steps:(map(. + {status:"todo"}) | .[0].status = "doing"), notes:[]}' > "$tmp" \
        && jq empty "$tmp"; then mv "$tmp" "$F"; else rm -f "$tmp"; die "생성 실패"; fi
    echo "생성: $(jq -r '.steps | length' "$F")단계, 진행 중 → $(jq -r '.steps[0] | "\(.id). \(.title)"' "$F")"
    ;;
  status)
    need
    jq -r '
      ([.steps[] | select(.status == "done")]    | length) as $d |
      ([.steps[] | select(.status == "blocked")] | length) as $b |
      "\(.task) — 완료 \($d)/\(.steps | length)" + (if $b > 0 then ", 막힘 \($b)" else "" end),
      "진행 중: " + (first(.steps[] | select(.status == "doing") | "\(.id). \(.title)") // "없음"),
      ((.notes // [])[-3:][] | "메모: " + .)' "$F"
    ;;
  steps)
    need
    jq -r '.steps[] | "\(.id)\t\(.status)\t\(.title)" + (if .note then "  (\(.note))" else "" end)' "$F"
    ;;
  done)
    need; [ $# -eq 1 ] || die "사용법: done <id>"; has_id "$1"
    apply --arg id "$1" "(.steps[] | select(.id == \$id)).status = \"done\" | $ADVANCE"
    "$0" status | sed -n 2p
    ;;
  block)
    need; [ $# -eq 2 ] || die '사용법: block <id> "<이유>"'; has_id "$1"
    apply --arg id "$1" --arg r "$2" \
      "(.steps[] | select(.id == \$id)) |= (.status = \"blocked\" | .note = \$r) | $ADVANCE"
    "$0" status | sed -n 2p
    ;;
  start)
    need; [ $# -eq 1 ] || die "사용법: start <id>"; has_id "$1"
    apply --arg id "$1" '(.steps[] | select(.status == "doing")).status = "todo"
                       | (.steps[] | select(.id == $id)).status = "doing"'
    "$0" status | sed -n 2p
    ;;
  add)
    need; [ $# -ge 2 ] || die '사용법: add <id> "<제목>" [<이 id 뒤에>]'
    jq -e --arg id "$1" 'any(.steps[]; .id == $id)' "$F" >/dev/null && die "이미 있는 id: $1"
    after="${3:-}"
    [ -n "$after" ] && has_id "$after"
    apply --arg id "$1" --arg t "$2" --arg a "$after" '
      {id:$id, title:$t, status:"todo"} as $s |
      if $a == "" then .steps += [$s]
      else (.steps | map(.id) | index($a)) as $i | .steps = .steps[:$i+1] + [$s] + .steps[$i+1:] end'
    echo "추가: $1. $2"
    ;;
  note)
    need; [ $# -eq 1 ] || die '사용법: note "<내용>"'
    apply --arg n "$1" '.notes = ((.notes // []) + [$n])'
    echo "메모 추가"
    ;;
  finish)
    need; rm -f "$F"; echo "progress.json 삭제됨"
    ;;
  *)
    die "알 수 없는 명령: $cmd (init|status|steps|done|block|start|add|note|finish)"
    ;;
esac
