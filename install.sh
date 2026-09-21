#!/usr/bin/env bash
# Genial Labs — instalador de terminal (Linux/macOS, bash 3.2+)
set -euo pipefail

REPO_GIT="https://github.com/brunao23/genial-labs.git"
ZIP_URL="https://codeload.github.com/brunao23/genial-labs/zip/refs/heads/main"

if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  C() { printf '\033[%sm%s\033[0m\n' "$1" "$2"; }
else
  C() { printf '%s\n' "$2"; }
fi
CYA="1;36"; BLU="1;34"; DIMC="2"; GRN="1;32"; RED="1;31"
die() { C "$RED" "erro: $1"; exit 1; }

G=("██████╗ " "██╔══██╗" "██████╔╝" "██╔══██╗" "██║  ██║" "╚═╝  ╚═╝")
E=("███████╗" "██╔════╝" "█████╗  " "██╔══╝  " "███████╗" "╚══════╝")
N=("███╗   ███╗" "████╗ ████║" "██╔████╔██║" "██║╚██╔╝██║" "██║ ╚═╝ ██║" "╚═╝     ╚═╝")
I=("███╗" "████╗" "██╔██║" "██║╚██║" "██║ ╚██║" "╚═╝  ╚═╝")
A=(" █████╗ " "██╔══██╗" "███████║" "██╔══██║" "██║  ██║" "╚═╝  ╚═╝")
L=("██╗     " "██║     " "██║     " "██║     " "███████╗" "╚══════╝")
B=("██████╗ " "██╔══██╗" "██████╔╝" "██╔═══██╗" "██║   ██║" "╚═╝   ╚═╝")
S=("███████╗" "██╔════╝" "█████╗  " "╚════╝  " "███████╗" "╚══════╝")
row() {
  printf '%s  %s  %s  %s  %s  %s   %s  %s  %s  %s' \
    "${G[$1]}" "${E[$1]}" "${N[$1]}" "${I[$1]}" "${A[$1]}" "${L[$1]}" \
    "${L[$1]}" "${A[$1]}" "${B[$1]}" "${S[$1]}"
}
banner() {
  echo
  i=0
  while [ $i -lt 6 ]; do C "$CYA" "$(row $i)"; i=$((i+1)); done
  C "$BLU" "    Genial Labs · arquitetura + dados + segurança + infra que guia seu código"
  C "$DIMC" "    instalador v1.0"
  echo
}

REPO_FLAG=""
while [ $# -gt 0 ]; do
  case "$1" in
    --repo) REPO_FLAG=1 ;;
    -h|--help) C 0 "Uso: install.sh [--repo]  (--repo instala a skill também nas skills do repositório atual)"; exit 0 ;;
    *) die "opção desconhecida: $1" ;;
  esac
  shift
done

banner

command -v python3 >/dev/null 2>&1 || die "python3 é obrigatório (o pacote usa apenas stdlib)."
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 7) else 1)' || die "python3 >= 3.7 necessário."
HAVE_GIT=0; command -v git >/dev/null 2>&1 && HAVE_GIT=1
HAVE_CURL=0; command -v curl >/dev/null 2>&1 && HAVE_CURL=1

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "[1/4] baixando o pacote…"
if [ "$HAVE_GIT" = "1" ]; then
  git clone --depth 1 "$REPO_GIT" "$TMP/pacote" >/dev/null 2>&1 || die "falha no git clone."
else
  if [ "$HAVE_CURL" = "1" ]; then
    curl -fsSL -o "$TMP/p.zip" "$ZIP_URL" || die "falha no download (curl)."
  else
    python3 -c 'import urllib.request,sys; urllib.request.urlretrieve(sys.argv[1], sys.argv[2])' "$ZIP_URL" "$TMP/p.zip" || die "falha no download."
  fi
  python3 -c 'import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])' "$TMP/p.zip" "$TMP/x" || die "falha ao extrair."
  mv "$TMP"/x/genial-labs-* "$TMP/pacote"
fi
[ -f "$TMP/pacote/genial" ] || die "pacote incompleto após o download."

echo "[2/4] instalando em ~/.genial-labs …"
rm -rf "$HOME/.genial-labs"
mkdir -p "$HOME/.genial-labs"
cp -R "$TMP/pacote/." "$HOME/.genial-labs/"

echo "[3/4] instalando a skill cidadela (Codex + Claude Code)…"
mkdir -p "$HOME/.agents/skills" "$HOME/.claude/skills"
rm -rf "$HOME/.agents/skills/cidadela" "$HOME/.claude/skills/cidadela"
cp -R "$HOME/.genial-labs/skills/cidadela" "$HOME/.agents/skills/cidadela"
cp -R "$HOME/.genial-labs/skills/cidadela" "$HOME/.claude/skills/cidadela"
if [ -n "$REPO_FLAG" ]; then
  mkdir -p ./.agents/skills ./.claude/skills
  cp -R "$HOME/.genial-labs/skills/cidadela" "./.agents/skills/cidadela"
  cp -R "$HOME/.genial-labs/skills/cidadela" "./.claude/skills/cidadela"
  C "$DIMC" "  + skill instalada também neste repositório (.agents/skills e .claude/skills)."
fi

echo "[4/4] instalando o comando 'genial'…"
mkdir -p "$HOME/.local/bin"
cp "$HOME/.genial-labs/genial" "$HOME/.local/bin/genial"
chmod +x "$HOME/.local/bin/genial"

case ":$PATH:" in
  *":$HOME/.local/bin:"*) : ;;
  *) C "$BLU" "aviso: adicione ao PATH  →  export PATH=\"\$HOME/.local/bin:\$PATH\"" ;;
esac

"$HOME/.local/bin/genial" banner >/dev/null 2>&1 || die "verificação do comando genial falhou."
SELFTEST="$TMP/selftest"
"$HOME/.local/bin/genial" init "$SELFTEST" --stack py >/dev/null 2>&1 || die "self-test 'genial init' falhou."
[ -f "$SELFTEST/ARCHITETURA-DADOS.md" ] || die "self-test incompleto."
rm -rf "$SELFTEST"

C "$GRN" "✓ Genial Labs instalado."
echo
C "$GRN" "  O que você ganhou:"
C 0 "   • skill 'cidadela' no Codex e no Claude Code (8 fases: diagnóstico → veredito → cirurgia → ofensiva → blindagem → plataforma)"
C 0 "   • comando 'genial': init (projeto guiado) · doctor (auditoria) · deploy (degrau de infra) · skills"
C 0 "   • templates de Arquitetura de Dados + Docker/Compose/K8s + gates de CI"
echo
C "$BLU" "  Primeiros passos:"
C 0 "   genial init meu-projeto --stack py    # novo projeto com arquitetura de dados embutida"
C 0 "   cd meu-projeto && genial doctor       # auditar um projeto existente"
C 0 "   genial deploy                         # onde você está na escada VPS→Docker→K8s→AWS"
echo
C "$DIMC" "  No Codex: /skills → cidadela — ou escreva: \"cidadela: audite este repositório\"."
echo
