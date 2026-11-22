#!/usr/bin/env bash
# PostToolUse hook for SolidCraft MCP calls: check exported laser DXFs (fabrication/tools/dxf_check.py).
# Acts only when the tool input names a `*_x<N>.dxf` path inside a project with fabrication.toml.
# FAILED or NOT CHECKED: exit 2, report on stderr (fed back to the agent). Otherwise silent, exit 0.
set -u
root="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$root" || exit 0

input="$(cat)"
mapfile -t files < <(printf '%s' "$input" | jq -r '.tool_input | .. | strings' 2>/dev/null \
  | grep -oE '[A-Za-z0-9_./-]+_x[0-9]+\.dxf' | sort -u)
[[ ${#files[@]} -eq 0 ]] && exit 0

declare -A by_project
for f in "${files[@]}"; do
  rel="${f#"$root"/}"
  project="${rel%%/*}"
  [[ -f "$project/fabrication.toml" && -f "$rel" ]] || continue
  by_project[$project]+="$rel "
done

rc=0
for project in "${!by_project[@]}"; do
  # shellcheck disable=SC2086
  out="$(DIRENV_LOG_FORMAT= direnv exec "$root" python3 fabrication/tools/dxf_check.py "$project" ${by_project[$project]} 2>&1)"
  status=$?
  if [[ $status -ne 0 ]]; then
    printf 'DXF check after export (just lamp-check):\n%s\n' "$out" >&2
    rc=2
  fi
done
exit $rc
