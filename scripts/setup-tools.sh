#!/usr/bin/env bash
# Downloads the tools used by scripts/validate.py into .tools/ (Linux/macOS).
#   luau-lsp  - type checks every ```luau code block against the Roblox API
#   stylua    - checks formatting of code blocks
#   Roblox type definitions from the luau-lsp repository
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOOLS="$ROOT/.tools"
mkdir -p "$TOOLS"
cd "$TOOLS"

case "$(uname -s)-$(uname -m)" in
	Linux-x86_64) LSP_ASSET="luau-lsp-linux-x86_64.zip"; STYLUA_ASSET="stylua-linux-x86_64.zip" ;;
	Linux-aarch64) LSP_ASSET="luau-lsp-linux-arm64.zip"; STYLUA_ASSET="stylua-linux-aarch64.zip" ;;
	Darwin-arm64) LSP_ASSET="luau-lsp-macos.zip"; STYLUA_ASSET="stylua-macos-aarch64.zip" ;;
	Darwin-x86_64) LSP_ASSET="luau-lsp-macos.zip"; STYLUA_ASSET="stylua-macos-x86_64.zip" ;;
	*) echo "Unsupported platform: $(uname -s)-$(uname -m)" >&2; exit 1 ;;
esac

fetch() { curl -fsSL --retry 3 -o "$2" "$1"; }

fetch "https://github.com/JohnnyMorganz/luau-lsp/releases/latest/download/$LSP_ASSET" luau-lsp.zip
fetch "https://github.com/JohnnyMorganz/StyLua/releases/latest/download/$STYLUA_ASSET" stylua.zip
unzip -o -q luau-lsp.zip
unzip -o -q stylua.zip
rm -f luau-lsp.zip stylua.zip
chmod +x luau-lsp stylua

fetch "https://raw.githubusercontent.com/JohnnyMorganz/luau-lsp/main/scripts/globalTypes.None.d.luau" globalTypes.d.luau

echo "Installed into $TOOLS:"
./luau-lsp --version
./stylua --version
