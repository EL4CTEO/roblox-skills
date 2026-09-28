# Supported agents

These skills use the open [Agent Skills](https://agentskills.io) format (`SKILL.md` folders), so any
agent that reads that format can use them. The table below lists the skill folders for each agent
that the installers know about.

## Install with `npx skills` (any agent, needs Node.js)

The [`skills` CLI](https://github.com/vercel-labs/skills) installs from this repository into more than
70 agents:

```bash
npx skills add EL4CTEO/roblox-skills                              # choose agents and skills interactively
npx skills add EL4CTEO/roblox-skills -a cursor -a windsurf -y     # into this project
npx skills add EL4CTEO/roblox-skills -a claude-code -g -y         # for your user
npx skills update                                                 # later: pull new versions
```

Its agent ids are listed in [its README](https://github.com/vercel-labs/skills#supported-agents). They
mostly match the ids below; Claude Code is `claude-code` and Copilot is `github-copilot`.

## Install with the scripts in this repository (no Node.js)

```bash
git clone https://github.com/EL4CTEO/roblox-skills.git && cd roblox-skills
./scripts/install.sh --project /path/to/game --agent windsurf     # macOS / Linux
./scripts/install.sh --global --agent agents --agent claude
.\scripts\install.ps1 -Project C:\games\my-game -Agent windsurf  # Windows PowerShell
./scripts/install.sh --list-agents                                 # print this table
```

`--agent` takes an id or an alias from the table, and can be repeated. Without `--agent`, the scripts
install into `.agents/skills`.

## Agents and folders

`$CONFIG` means `$XDG_CONFIG_HOME`, or `~/.config` when it is not set.

| Agent | `--agent` (aliases) | Project folder | Global folder |
| --- | --- | --- | --- |
| Codex, Cline, Warp, Zed, Kimi Code; in projects also Cursor, Gemini CLI, Copilot, OpenCode, Amp, Kilo Code, Droid, Antigravity | `agents` (`universal`, `codex`, `cline`, `warp`, `zed`, `kimi`) | `.agents/skills` | `~/.agents/skills` |
| Claude Code | `claude` (`claude-code`) | `.claude/skills` | `~/.claude/skills` |
| Cursor | `cursor` | `.agents/skills` | `~/.cursor/skills` |
| OpenCode | `opencode` | `.opencode/skills` | `$CONFIG/opencode/skills` |
| Gemini CLI | `gemini` (`gemini-cli`) | `.gemini/skills` | `~/.gemini/skills` |
| GitHub Copilot (CLI, VS Code, coding agent) | `copilot` (`github-copilot`) | `.github/skills` | `~/.copilot/skills` |
| Google Antigravity | `antigravity` | `.agents/skills` | `~/.gemini/antigravity/skills` |
| Amp | `amp` | `.agents/skills` | `$CONFIG/agents/skills` |
| Kilo Code | `kilo` (`kilocode`) | `.agents/skills` | `~/.kilo/skills` |
| Factory Droid | `droid` (`factory`) | `.agents/skills` | `~/.factory/skills` |
| Windsurf | `windsurf` | `.windsurf/skills` | `~/.codeium/windsurf/skills` |
| Roo Code | `roo` (`roo-code`) | `.roo/skills` | `~/.roo/skills` |
| Kiro | `kiro` (`kiro-cli`) | `.kiro/skills` | `~/.kiro/skills` |
| JetBrains Junie | `junie` | `.junie/skills` | `~/.junie/skills` |
| Goose | `goose` | `.goose/skills` | `$CONFIG/goose/skills` |
| Qwen Code | `qwen` (`qwen-code`) | `.qwen/skills` | `~/.qwen/skills` |
| Continue | `continue` | `.continue/skills` | `~/.continue/skills` |
| Crush | `crush` | `.crush/skills` | `$CONFIG/crush/skills` |
| Trae | `trae` | `.trae/skills` | `~/.trae/skills` |
| Augment | `augment` | `.augment/skills` | `~/.augment/skills` |
| OpenHands | `openhands` | `.openhands/skills` | `~/.openhands/skills` |
| Devin for Terminal | `devin` | `.devin/skills` | `$CONFIG/devin/skills` |
| Mistral Vibe | `vibe` (`mistral-vibe`) | `.vibe/skills` | `~/.vibe/skills` |
| Qoder | `qoder` | `.qoder/skills` | `~/.qoder/skills` |
| CodeBuddy | `codebuddy` | `.codebuddy/skills` | `~/.codebuddy/skills` |
| Tabnine CLI | `tabnine` (`tabnine-cli`) | `.tabnine/agent/skills` | `~/.tabnine/agent/skills` |
| Atlassian Rovo Dev | `rovodev` | `.rovodev/skills` | `~/.rovodev/skills` |
| iFlow CLI | `iflow` (`iflow-cli`) | `.iflow/skills` | `~/.iflow/skills` |
| Pi | `pi` | `.pi/skills` | `~/.pi/agent/skills` |

Many agents also read other agents' folders (for example, OpenCode and Copilot read `.claude/skills`).
Install into one folder per agent to avoid duplicate skills. Restart the agent or start a new session
after installing.

Two more ways to install:

- **Claude Code plugin**: `/plugin marketplace add EL4CTEO/roblox-skills`, then
  `/plugin install roblox-skills@roblox-skills`.
- **Roblox Studio Assistant**: download `roblox-assistant-skills.zip` from the
  [latest release](https://github.com/EL4CTEO/roblox-skills/releases/latest) and paste a file into
  **Assistant → Settings → Skills → Add**.

Is your agent missing, or is a folder wrong? Open an issue or edit `scripts/agents.tsv`, which both
installers read, and update this table.
