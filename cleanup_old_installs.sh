#!/usr/bin/env bash
# Preview-first cleanup for SDS100 Monitor installs.
# Keeps only the newest installed version (plus any given with --keep) and
# removes every older program folder and menu launcher.
# Never touches reception history or other data: ~/SDS100Monitor,
# ~/SDS100MonitorData and all CSV, HPDB and Favorites List files are left alone.
set -euo pipefail

usage() {
  echo "Usage: bash $0 [--keep VERSION]... [--delete]" >&2
  echo "  Without --delete, only lists what would be removed." >&2
  echo "  --keep VERSION also keeps that version, e.g. --keep 24 or --keep 1.1.14" >&2
  exit 2
}

delete=0
keep=()
while (($#)); do
  case "$1" in
    --delete) delete=1;;
    --keep) [[ $# -ge 2 ]] || usage; keep+=("${2#[Vv]}"); shift;;
    *) usage;;
  esac
  shift
done

shopt -s nullglob
apps="$HOME/.local/share/applications"
paths=(); versions=()

# Record a recognized install folder or launcher with its version.
add() { paths+=("$1"); versions+=("$2"); }

for path in "$HOME"/SDS100MonitorV* "$HOME"/SDS100Monitorv* "$HOME"/SDS100Monitor-[0-9]*; do
  [[ -d "$path" && ! -L "$path" ]] || continue
  name=${path##*/}
  if [[ "$name" =~ ^SDS100Monitor[Vv]([0-9]+)($|[_-].*) ]]; then
    add "$path" "$((10#${BASH_REMATCH[1]}))"
  elif [[ "$name" =~ ^SDS100Monitor-([0-9]+\.[0-9]+\.[0-9]+)(-personal)?$ ]]; then
    add "$path" "${BASH_REMATCH[1]}"
  fi
done
if [[ -d "$apps" ]]; then
  for path in "$apps"/sds100-monitor-v*.desktop "$apps"/sds100-monitor-V*.desktop "$apps"/sds100-monitor-[0-9]*.desktop; do
    [[ -f "$path" || -L "$path" ]] || continue
    name=${path##*/}
    if [[ "$name" =~ ^sds100-monitor-[Vv]([0-9]+)([-_].*)?\.desktop$ ]]; then
      add "$path" "$((10#${BASH_REMATCH[1]}))"
    elif [[ "$name" =~ ^sds100-monitor-([0-9]+\.[0-9]+\.[0-9]+)(-personal)?\.desktop$ ]]; then
      add "$path" "${BASH_REMATCH[1]}"
    fi
  done
fi

if ((${#paths[@]} == 0)); then
  echo 'No SDS100 Monitor installs found.'
  exit 0
fi

# Sort key: the old V-numbered builds (V9, V24...) are older than every
# dotted 1.x.y build, so prefix them with 0. and dotted versions with 1.
sort_key() { if [[ "$1" == *.* ]]; then echo "1.$1"; else echo "0.$1"; fi; }
latest_key=$(for v in "${versions[@]}"; do sort_key "$v"; done | sort -V | tail -n 1)
# Installed from the .deb (v1.1.53 and later): every folder install in your home is older.
deb_dir="${SDS100_MONITOR_DEB_DIR:-/opt/sds100-monitor}"
if [[ -f "$deb_dir/sds100_monitor.py" ]]; then
  latest_key="installed-package"
  printf 'SDS100 Monitor is installed as a package (%s), so all folder installs below are older.\n' "$deb_dir"
fi

remove=(); kept=(); labels=()
for i in "${!paths[@]}"; do
  v=${versions[$i]}
  label=$([[ "$v" == *.* ]] && echo "v$v" || echo "V$v")
  if [[ "$(sort_key "$v")" == "$latest_key" ]]; then
    kept+=("${paths[$i]}  ($label, newest)")
  elif [[ " ${keep[*]-} " == *" $v "* ]]; then
    kept+=("${paths[$i]}  ($label, --keep)")
  else
    remove+=("${paths[$i]}")
    labels+=("$label")
  fi
done

printf '\nSDS100 Monitor cleanup — %s\n' "$( ((delete)) && echo DELETE || echo PREVIEW )"
printf 'Your reception history (~/SDS100Monitor) and all CSV, HPDB and Favorites List\nfiles are never touched.\n\n'
printf 'KEEPING:\n'; printf '  %s\n' "${kept[@]}"
if ((${#remove[@]} == 0)); then
  printf '\nNothing older to remove.\n'
  exit 0
fi
printf '\nOLDER VERSIONS TO REMOVE:\n'
for i in "${!remove[@]}"; do printf '  %s  (%s)\n' "${remove[$i]}" "${labels[$i]}"; done
for v in "${versions[@]}"; do
  if [[ "$v" == 24 && " ${keep[*]-} " != *" 24 "* ]]; then
    printf '\nNote: V24 is the last version with the database/favorites panel. To keep it,\nadd --keep 24.\n'
    break
  fi
done

if ((!delete)); then
  printf '\nPREVIEW ONLY — nothing removed. To remove the items listed above, run:\n  bash "%s" --delete' "$0"
  for v in "${keep[@]-}"; do [[ -n "$v" ]] && printf ' --keep %s' "$v"; done
  printf '\n'
  exit 0
fi

printf '\nWARNING: these folders and launchers will be permanently removed.\n'
read -r -p 'Type DELETE OLD VERSIONS to proceed: ' answer
[[ "$answer" == 'DELETE OLD VERSIONS' ]] || { echo 'Cancelled.'; exit 0; }
for path in "${remove[@]}"; do
  # Re-check every path against the strict patterns before removing it.
  [[ "$path" == "$HOME"/* ]] || continue
  name=${path##*/}
  if [[ "$path" == "$apps"/* ]]; then
    [[ "$name" =~ ^sds100-monitor-([Vv][0-9]+([-_].*)?|[0-9]+\.[0-9]+\.[0-9]+(-personal)?)\.desktop$ ]] || continue
    rm -f -- "$path"
  else
    [[ "$name" =~ ^SDS100Monitor([Vv][0-9]+($|[_-].*)|-[0-9]+\.[0-9]+\.[0-9]+(-personal)?)$ ]] || continue
    [[ -d "$path" && ! -L "$path" ]] || continue
    rm -rf -- "$path"
  fi
  echo "Removed: $path"
done
echo 'Cleanup complete.'
