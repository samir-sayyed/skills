#!/bin/bash
# transcript.sh <youtube-url> <out.txt> — YouTube captions → plain text
set -uo pipefail
url="$1"; out="$2"; tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

# ponytail: a dead/private URL costs ~2min of yt-dlp retries before erroring.
# Fine for the 06:57 unattended run; add gtimeout if a queue ever stalls on it.
yt-dlp --socket-timeout 15 --retries 2 --skip-download \
       --write-sub --write-auto-sub --sub-lang "en.*" --sub-format vtt \
       -o "$tmp/s" --print-to-file title "$tmp/title.txt" "$url" >/dev/null || true

f=$(ls "$tmp"/s.*.vtt 2>/dev/null | head -1)
[ -n "$f" ] || { echo "no captions: $url" >&2; exit 1; }

# VTT → prose: drop headers/cues, strip inline <c> karaoke tags, drop the
# rolling-window duplicate lines auto-captions emit.
{ echo "# $(cat "$tmp/title.txt")"; echo "# $url"; echo
  grep -vE '^(WEBVTT|Kind:|Language:|[0-9]{2}:|$)' "$f" \
    | sed 's/<[^>]*>//g;s/^ *//;s/ *$//' \
    | awk 'NF && !seen[$0]++'; } > "$out"

# the check: parsing that silently produces near-nothing must fail loudly
[ "$(wc -w < "$out")" -gt 100 ] || { echo "transcript too short, parse likely broke: $out" >&2; exit 1; }
