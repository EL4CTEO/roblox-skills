#!/usr/bin/env bash
# Install Roblox skills for AI coding agents.
#
#   ./scripts/install.sh [options] [skill ...]
#
# Options:
#   -a, --agent NAME   Target agent (repeatable). One of:
#                        agents    .agents/skills   (Codex, Gemini CLI, GitHub Copilot, OpenCode, Cursor) [default]
#                        claude    .claude/skills   (Claude Code; also read by OpenCode and Copilot)
#                        opencode  .opencode/skills (project) / ~/.config/opencode/skills (global)
#                        gemini    .gemini/skills
#                        copilot   .github/skills (project) / ~/.copilot/skills (global)
#   -g, --global       Install for your user (home directory) instead of a project.
#   -p, --project DIR  Project directory to install into (default: current directory).
#   -l, --link         Symlink instead of copying (updates when you `git pull` this repo).
#   -f, --force        Replace existing skills with the same name.
#   -h, --help         Show this help.
#
# Examples:
#   ./scripts/install.sh --agent claude --global
#   ./scripts/install.sh --project ~/games/my-obby roblox-luau roblox-security
#   ./scripts/install.sh --agent agents --agent claude --link --global
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$ROOT/skills"

agents=()
global=false
project="$PWD"
link=false
force=false
selected=()

usage() { sed -n '2,24p' "$0" | sed 's/^# \{0,1\}//'; }

while [[ $# -gt 0 ]]; do
	case "$1" in
		-a|--agent) agents+=("$2"); shift 2 ;;
		-g|--global) global=true; shift ;;
		-p|--project) project="$2"; shift 2 ;;
		-l|--link) link=true; shift ;;
		-f|--force) force=true; shift ;;
		-h|--help) usage; exit 0 ;;
		-*) echo "Unknown option: $1" >&2; usage; exit 1 ;;
		*) selected+=("$1"); shift ;;
	esac
done

[[ ${#agents[@]} -eq 0 ]] && agents=("agents")

target_dir() {
	local agent="$1"
	if $global; then
		case "$agent" in
			agents) echo "$HOME/.agents/skills" ;;
			claude) echo "$HOME/.claude/skills" ;;
			opencode) echo "${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills" ;;
			gemini) echo "$HOME/.gemini/skills" ;;
			copilot) echo "$HOME/.copilot/skills" ;;
			*) return 1 ;;
		esac
	else
		case "$agent" in
			agents) echo "$project/.agents/skills" ;;
			claude) echo "$project/.claude/skills" ;;
			opencode) echo "$project/.opencode/skills" ;;
			gemini) echo "$project/.gemini/skills" ;;
			copilot) echo "$project/.github/skills" ;;
			*) return 1 ;;
		esac
	fi
}

if [[ ${#selected[@]} -eq 0 ]]; then
	for dir in "$SKILLS_DIR"/*/; do
		selected+=("$(basename "$dir")")
	done
fi

for name in "${selected[@]}"; do
	if [[ ! -f "$SKILLS_DIR/$name/SKILL.md" ]]; then
		echo "Unknown skill: $name (see $SKILLS_DIR)" >&2
		exit 1
	fi
done

for agent in "${agents[@]}"; do
	if ! dest="$(target_dir "$agent")"; then
		echo "Unknown agent: $agent" >&2
		exit 1
	fi
	mkdir -p "$dest"
	installed=0
	skipped=0
	for name in "${selected[@]}"; do
		src="$SKILLS_DIR/$name"
		out="$dest/$name"
		if [[ -e "$out" || -L "$out" ]]; then
			if ! $force; then
				skipped=$((skipped + 1))
				continue
			fi
			rm -rf "$out"
		fi
		if $link; then
			ln -s "$src" "$out"
		else
			cp -R "$src" "$out"
		fi
		installed=$((installed + 1))
	done
	echo "$agent: installed $installed skill(s) into $dest$( ((skipped > 0)) && echo " ($skipped already present; use --force to replace)")"
done

cat <<'EOF'

Done. Restart your agent (or start a new session) so it discovers the skills.
Tip: agents like OpenCode and GitHub Copilot read several directories; install to one of them only
to avoid duplicate skills. Claude Code users can also install the plugin:
  /plugin marketplace add EL4CTEO/roblox-skills
  /plugin install roblox-skills@roblox-skills
EOF
