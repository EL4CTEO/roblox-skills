#!/usr/bin/env bash
# Install Roblox skills for AI coding agents.
#
#   ./scripts/install.sh [options] [skill ...]
#
# Options:
#   -a, --agent NAME   Target agent (repeatable). Default: agents (.agents/skills, the shared folder
#                      read by Codex, Cursor, Gemini CLI, Copilot, OpenCode, Amp, Cline and more).
#                      Others: claude, cursor, opencode, gemini, copilot, windsurf, roo, kiro, junie,
#                      goose, qwen, continue, crush, trae, augment, openhands, ... (see --list-agents).
#   -g, --global       Install for your user (home directory) instead of a project.
#   -p, --project DIR  Project directory to install into (default: current directory).
#   -l, --link         Symlink instead of copying (updates when you `git pull` this repo).
#   -f, --force        Replace existing skills with the same name.
#       --list-agents  Show every supported agent and its skill directories.
#   -h, --help         Show this help.
#
# Examples:
#   ./scripts/install.sh --agent claude --global
#   ./scripts/install.sh --project ~/games/my-obby roblox-luau roblox-security
#   ./scripts/install.sh --agent agents --agent windsurf --link --global
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$ROOT/skills"
AGENTS_TSV="$ROOT/scripts/agents.tsv"

agents=()
global=false
project="$PWD"
link=false
force=false
selected=()

usage() { sed -n '2,22p' "$0" | sed 's/^# \{0,1\}//'; }

list_agents() {
	printf '%-12s %-26s %-34s %s\n' AGENT PROJECT GLOBAL TOOLS
	grep -v '^#' "$AGENTS_TSV" | while IFS=$'\t' read -r id _ proj glob tools; do
		printf '%-12s %-26s %-34s %s\n' "$id" "$proj" "$glob" "$tools"
	done
}

while [[ $# -gt 0 ]]; do
	case "$1" in
		-a|--agent) agents+=("$2"); shift 2 ;;
		-g|--global) global=true; shift ;;
		-p|--project) project="$2"; shift 2 ;;
		-l|--link) link=true; shift ;;
		-f|--force) force=true; shift ;;
		--list-agents) list_agents; exit 0 ;;
		-h|--help) usage; exit 0 ;;
		-*) echo "Unknown option: $1" >&2; usage; exit 1 ;;
		*) selected+=("$1"); shift ;;
	esac
done

[[ ${#agents[@]} -eq 0 ]] && agents=("agents")

# Print the skills directory for an agent id or alias; fail if unknown.
target_dir() {
	local agent="$1" id aliases proj glob _tools
	while IFS=$'\t' read -r id aliases proj glob _tools; do
		[[ "$id" == \#* || -z "$id" ]] && continue
		if [[ "$agent" == "$id" || ",$aliases," == *",$agent,"* ]]; then
			if $global; then
				glob="${glob/#\~/$HOME}"
				echo "${glob/#\$CONFIG/${XDG_CONFIG_HOME:-$HOME/.config}}"
			else
				echo "$project/$proj"
			fi
			return 0
		fi
	done <"$AGENTS_TSV"
	return 1
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
		echo "Unknown agent: $agent (run with --list-agents)" >&2
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
Tip: many agents read several directories (for example .agents/skills and their own); install to one
of them only to avoid duplicate skills. Claude Code users can also install the plugin:
  /plugin marketplace add EL4CTEO/roblox-skills
  /plugin install roblox-skills@roblox-skills
EOF
