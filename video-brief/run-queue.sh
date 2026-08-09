#!/bin/zsh
# Daily runner for the video-brief skill. Invoked by launchd at 06:57.
# Does nothing at all when the queue holds no URLs.

export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/bin:/bin"

QUEUE="$HOME/video-queue.txt"
LOG="$HOME/.video-brief.log"

grep -qE '^[[:space:]]*https?://' "$QUEUE" || exit 0

print "\n===== $(date '+%Y-%m-%d %H:%M') =====" >> "$LOG"

# ponytail: scoped allowlist rather than --dangerously-skip-permissions.
# If a run dies on a denied tool, widen this list — don't reach for the skip flag.
claude -p "Use the video-brief skill to process the queue at ~/video-queue.txt." \
  --allowedTools "Bash,Read,Write,Edit,Artifact,Skill" \
  >> "$LOG" 2>&1
