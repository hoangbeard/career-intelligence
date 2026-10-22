#!/usr/bin/env bash
# Block commits containing employer-identifying strings.
# Patterns live outside the repo (one ERE per line, '#' comments allowed):
#   ${SANITIZE_DENYLIST:-~/.config/sanitize-denylist}
# The file is private on purpose: publishing the list would leak what it protects.
set -euo pipefail

denylist="${SANITIZE_DENYLIST:-$HOME/.config/sanitize-denylist}"
if [[ ! -f "$denylist" ]]; then
  echo "sanitize-denylist: $denylist not found, skipping (set SANITIZE_DENYLIST to enable)" >&2
  exit 0
fi

patterns=$(grep -vE '^\s*(#|$)' "$denylist" || true)
[[ -z "$patterns" ]] && exit 0

# A private instance (marked by .career-intelligence-instance) holds the owner's own
# history under data/, employer names included. Check only the other files.
instance=false
[[ -f .career-intelligence-instance ]] && instance=true

status=0
for file in "$@"; do
  [[ -f "$file" ]] || continue
  if $instance && [[ $file == data/* ]]; then continue; fi
  if matches=$(grep -inIE -f <(printf '%s\n' "$patterns") -- "$file"); then
    echo "sanitize-denylist: blocked content in $file" >&2
    # Print line numbers only, never the matched text.
    cut -d: -f1 <<<"$matches" | sed "s|^|  line |" >&2
    status=1
  fi
done
exit $status
