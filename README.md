# Roblox Skills for AI Agents

[![Validate](https://github.com/EL4CTEO/roblox-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/EL4CTEO/roblox-skills/actions/workflows/validate.yml)
[![Release](https://img.shields.io/github/v/release/EL4CTEO/roblox-skills)](https://github.com/EL4CTEO/roblox-skills/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

23 [Agent Skills](https://agentskills.io) that keep AI agents' Roblox code current, secure, and
correct. They work with Claude Code, OpenCode, Codex, Cursor, Gemini CLI, GitHub Copilot, and Roblox
Studio Assistant.

- **Current**: checked against Roblox's API reference (Studio 0.740, September 2026). No `wait()`,
  `BodyVelocity`, or legacy `Chat`.
- **Verified**: CI type-checks every Luau example against the Roblox API (strict mode, new type solver)
  and flags deprecated APIs. A weekly run catches new deprecations.
- **Efficient**: agents see only a short description per skill (~150 tokens) and load the full skill
  on demand.

## Install

**Claude Code**

```text
/plugin marketplace add EL4CTEO/roblox-skills
/plugin install roblox-skills@roblox-skills
```

**Other agents**

```bash
git clone https://github.com/EL4CTEO/roblox-skills.git && cd roblox-skills
./scripts/install.sh --project /path/to/game       # .agents/skills (Codex, Gemini, Copilot, OpenCode, Cursor)
./scripts/install.sh --agent claude --global       # ~/.claude/skills
```

`--agent` also accepts `opencode`, `gemini`, and `copilot`. Add `--link` to symlink the skills so
`git pull` updates them. On Windows, use `scripts\install.ps1`.

**Roblox Studio Assistant**: download `roblox-assistant-skills.zip` from the
[latest release](https://github.com/EL4CTEO/roblox-skills/releases/latest), or run
`python3 scripts/build-assistant.py`. Then paste a file into **Assistant → Settings → Skills → Add**.

## Skills

| Area | Skills |
| --- | --- |
| Code and structure | `roblox-luau`, `roblox-architecture`, `roblox-networking`, `roblox-security`, `roblox-code-review` |
| Data and business | `roblox-data-stores`, `roblox-monetization`, `roblox-analytics-liveops`, `roblox-open-cloud` |
| Gameplay | `roblox-game-systems`, `roblox-characters-animation`, `roblox-npc-ai`, `roblox-physics`, `roblox-input` |
| Presentation | `roblox-ui`, `roblox-audio`, `roblox-world-building`, `roblox-text-chat` |
| Scale and workflow | `roblox-performance`, `roblox-teleport-matchmaking`, `roblox-tooling`, `roblox-testing`, `roblox-studio-mcp` |

Each skill lives in [`skills/`](skills/). For best results, also connect your agent to Studio's
built-in MCP server (see [`roblox-studio-mcp`](skills/roblox-studio-mcp/SKILL.md)) so it can playtest
and verify its changes.

## Contributing

```bash
./scripts/setup-tools.sh && python3 scripts/validate.py
```

See [CONTRIBUTING.md](CONTRIBUTING.md). Corrections are welcome whenever Roblox changes an API.

[MIT](LICENSE). This project is not affiliated with Roblox Corporation.
