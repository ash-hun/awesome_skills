#!/usr/bin/env bash
#
# Inject the humanism_talk `brief` rules into a session.
#
# Registered by `awesome-skills brief on` as a SessionStart and PostCompact hook.
# Pass the event name as the first argument; it goes back out in the JSON payload.
#
# Opt out without unregistering the hook by creating either of these files:
#   <project>/.claude/humanism_talk.off   — this project only
#   ~/.claude/humanism_talk.off           — everywhere

set -uo pipefail

EVENT="${1:-SessionStart}"
HOME_DIR="${AWESOME_SKILLS_HOME:-$HOME/.awesome-skills}"
BRIEF="$HOME_DIR/.claude/skills/humanism_talk/references/brief.md"

if [ -f "${CLAUDE_PROJECT_DIR:-$PWD}/.claude/humanism_talk.off" ]; then exit 0; fi
if [ -f "$HOME/.claude/humanism_talk.off" ]; then exit 0; fi
if [ ! -f "$BRIEF" ]; then exit 0; fi
if ! command -v jq >/dev/null 2>&1; then exit 0; fi

if [ "$EVENT" = "PostCompact" ]; then
  LEAD="압축 이후에도 아래 규칙을 계속 적용한다."
else
  LEAD="이번 세션 전체에 아래 규칙을 적용한다. 해제 조건은 규칙의 지속성 항목을 따른다."
fi

# Skip the reference file's own header — everything after the first horizontal rule.
awk 'f {print} /^---$/ {f=1}' "$BRIEF" \
  | jq -Rs --arg event "$EVENT" --arg lead "$LEAD" '{
      hookSpecificOutput: {
        hookEventName: $event,
        additionalContext: ("<humanism-talk-brief>\n" + $lead + "\n" + . + "\n</humanism-talk-brief>")
      },
      suppressOutput: true
    }'
