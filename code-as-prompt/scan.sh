#!/usr/bin/env bash
# Grep the four mechanical "code as prompt" smells. Judgement calls stay in SKILL.md.
# ponytail: regex, not a parser — misses smells inside strings/heredocs and over-reports
# in commented-out prose. Reach for tree-sitter only if the noise actually costs you time.
set -uo pipefail

APOLOGY='(hack(y|ish)?|temporar(y|ily)|fix (this )?later|for now|XXX|FIXME|kludge|band[- ]?aid)'
# a comment line whose body still looks like code
DEADCODE='^[[:space:]]*(//|#)[[:space:]]*([a-zA-Z_$][a-zA-Z0-9_$.<>]*[[:space:]]*[({=]|(return|if|for|while|import|fun|def|val|var|let|const|class)\b)'
TRAINWRECK='\)\.[a-zA-Z_][a-zA-Z0-9_]*\(\)\.[a-zA-Z_][a-zA-Z0-9_]*\('
LONG=300

selftest() {
  d=$(mktemp -d) && trap 'rm -rf "$d"' RETURN
  cat >"$d/f.kt" <<'EOF'
// hacky, fix this later
val x = compute()
// val old = legacy()
// this is a normal prose comment
val z = a.b().c().d()
EOF
  out=$("$0" "$d" 2>&1)
  for want in "hacky" "val old = legacy" "a.b().c().d"; do
    grep -qF "$want" <<<"$out" || { echo "FAIL: missed $want"; echo "$out"; exit 1; }
  done
  grep -qF "normal prose" <<<"$out" && { echo "FAIL: flagged prose comment"; exit 1; }
  echo "selftest ok"; exit 0
}
[ "${1:-}" = "--selftest" ] && selftest

TARGET="${1:-.}"
[ -e "$TARGET" ] || { echo "no such path: $TARGET" >&2; exit 1; }

section() { printf '\n== %s ==\n' "$1"; }
# prose files excluded: '#' is a heading there, not a comment marker
hits() { grep -rInE --exclude-dir={.git,node_modules,build,vendor,dist} \
  --exclude={'*.md','*.txt','*.rst','*.mdx'} "$1" "$TARGET" 2>/dev/null | head -40; }

section "1. apologetic comments — delete or reword"
hits "(//|#|/\*).*$APOLOGY" || true

section "2. commented-out code — delete it"
hits "$DEADCODE" || true

section "3. train wrecks — flatten, and name the result locally"
hits "$TRAINWRECK" || true

section "4. files past $LONG lines — split into a context directory"
find "$TARGET" -type f -size -2M \
  -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/build/*' \
  -not -path '*/vendor/*' -not -path '*/dist/*' \
  -exec awk -v n=$LONG 'END{if(FNR>n) printf "%6d  %s\n", FNR, FILENAME}' {} \; 2>/dev/null | sort -rn | head -20

printf '\nMutate-and-return functions are not greppable — read them. Start with whichever\n'
printf 'function the agent keeps failing on. See SKILL.md check 4.\n'
