#!/usr/bin/env bash
set -euo pipefail
H="$HOME"
ALVOS=("$H/.genial-labs" "$H/.local/bin/genial" "$H/.agents/skills/cidadela" "$H/.claude/skills/cidadela")
Y=0
[ "${1:-}" = "-y" ] && Y=1
for x in "${ALVOS[@]}"; do [ -e "$x" ] && echo "Remover: $x"; done
if [ "$Y" != "1" ] && [ -t 0 ]; then
  read -r -p "Confirmar? [s/N] " r
  case "$r" in s|sim|y|yes) ;; *) echo "Cancelado."; exit 0;; esac
fi
for x in "${ALVOS[@]}"; do
  if [ -e "$x" ]; then
    if [ -d "$x" ] && [ ! -L "$x" ]; then rm -rf "$x"; else rm -f "$x"; fi
    echo "  removido: $x"
  fi
done
echo "Genial Labs removido."
