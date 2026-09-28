# Roblox Skills for AI Agents

[![Validate skills](https://github.com/EL4CTEO/roblox-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/EL4CTEO/roblox-skills/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A complete, **up-to-date**, and **verified** set of [Agent Skills](https://agentskills.io) for Roblox
development. It works with **Claude Code, OpenCode, OpenAI Codex, Cursor, Gemini CLI, GitHub Copilot**,
and any other agent that supports the `SKILL.md` format. You can also build single-file versions for
**Roblox Studio Assistant**.

Coding agents often write Roblox code from stale memory: `wait()`, `BodyVelocity`, `FindPartOnRay`,
`LoadCharacter`, `SetPrimaryPartCFrame`, the legacy `Chat`, remotes that trust the client, and
DataStore code that duplicates items. These skills fix that. They teach current engine APIs (checked
against Roblox's docs as of **September 2026, Studio 0.740**), secure client/server design, and the
modern toolchain.

## Why these skills

- **Verified.** CI type-checks every Luau example (100+) with `luau-lsp`, using the new type solver in
  strict mode against the current Roblox API definitions. CI also checks formatting with StyLua and scans
  for 90+ deprecated or superseded APIs. A weekly run catches APIs that Roblox deprecates later.
- **Current.** The skills cover recent platform changes: the new type solver, require-by-string, the Input
  Action System, `UnreliableRemoteEvent`, the server authority model, StyleSheets, the Audio API,
  experience configs and experiments, the built-in Studio MCP server, the Character Controller Library,
  SLIM streaming, the 2025–2026 DataStore limits, and the `*Async` API renames.
- **Efficient.** The skills use progressive disclosure. The agent sees only short descriptions (about
  150 tokens per skill) until a task matches. Then it loads that skill's `SKILL.md` (about 2–5k tokens),
  and it opens the deeper `references/` files only when it needs them.
- **Practical.** Each skill gives defaults, copy-ready patterns, checklists, and anti-patterns. The
  skills link to each other by name, so an agent can move from networking to security to data stores.

## Skills

| Skill | Covers |
| --- | --- |
| [roblox-luau](skills/roblox-luau/SKILL.md) | Modern Luau, strict typing with the new solver, the `task` library, require-by-string, modules/OOP, error handling, buffers |
| [roblox-architecture](skills/roblox-architecture/SKILL.md) | Client/server model, where code goes, bootstrapping, player lifecycle, tag components, streaming-safe code |
| [roblox-networking](skills/roblox-networking/SKILL.md) | RemoteEvent / UnreliableRemoteEvent / RemoteFunction, serialization rules, bandwidth, synced time |
| [roblox-security](skills/roblox-security/SKILL.md) | Remote validation (NaN, spoofing), rate limiting, prompt abuse, ownership, combat and economy exploits, bans |
| [roblox-data-stores](skills/roblox-data-stores/SKILL.md) | ProfileStore and session locking, `UpdateAsync`, limits, migrations, leaderboards, MemoryStore, MessagingService |
| [roblox-monetization](skills/roblox-monetization/SKILL.md) | Idempotent `ProcessReceipt`, passes, subscriptions, rewarded ads, personalized shops, regional pricing, policy |
| [roblox-ui](skills/roblox-ui/SKILL.md) | Responsive layouts, safe areas, flex, StyleSheets, cross-platform navigation, React-lua/Fusion/Vide |
| [roblox-input](skills/roblox-input/SKILL.md) | Input Action System, UserInputService, `PreferredInput`, custom cameras |
| [roblox-physics](skills/roblox-physics/SKILL.md) | Raycasts and shapecasts, collision groups, mover constraints, ownership, server authority |
| [roblox-characters-animation](skills/roblox-characters-animation/SKILL.md) | Humanoids, damage, appearance, Animator, tweens, tools, the Character Controller Library |
| [roblox-npc-ai](skills/roblox-npc-ai/SKILL.md) | Pathfinding, chase loops, state machines, perception, scaling to many NPCs |
| [roblox-performance](skills/roblox-performance/SKILL.md) | MicroProfiler, memory leaks, rendering and physics cost, native codegen, Parallel Luau |
| [roblox-tooling](skills/roblox-tooling/SKILL.md) | Script Sync vs Rojo, Rokit, Wally/pesde, luau-lsp, StyLua, selene, Lune, roblox-ts, CI |
| [roblox-testing](skills/roblox-testing/SKILL.md) | Testable design, Jest Lua, running tests in Studio, through MCP, and in the cloud, QA checklist |
| [roblox-open-cloud](skills/roblox-open-cloud/SKILL.md) | Open Cloud APIs, HttpService and Secrets, publishing, Luau execution, webhooks |
| [roblox-studio-mcp](skills/roblox-studio-mcp/SKILL.md) | Connecting agents to Studio's built-in MCP server; explore → edit → playtest → verify |
| [roblox-audio](skills/roblox-audio/SKILL.md) | Audio API wiring, classic `Sound`, 2D/3D audio, mixing, asset permissions |
| [roblox-text-chat](skills/roblox-text-chat/SKILL.md) | TextChatService, required text filtering, chat commands and channels, PolicyService |
| [roblox-teleport-matchmaking](skills/roblox-teleport-matchmaking/SKILL.md) | `TeleportAsync`, reserved servers, lobbies and parties, matchmaking signals |
| [roblox-analytics-liveops](skills/roblox-analytics-liveops/SKILL.md) | AnalyticsService events, configs, A/B experiments, badges, notifications, live events |
| [roblox-world-building](skills/roblox-world-building/SKILL.md) | Parts and models, lighting, terrain, in-game CSG and destruction, procedural models, effects |
| [roblox-game-systems](skills/roblox-game-systems/SKILL.md) | Recipes: currency, levels, round loops, validated combat, inventory, shops, checkpoints, rewards |
| [roblox-code-review](skills/roblox-code-review/SKILL.md) | Review checklist by severity, plus a full map of deprecated and superseded APIs |

## Install

### Claude Code (plugin)

```text
/plugin marketplace add EL4CTEO/roblox-skills
/plugin install roblox-skills@roblox-skills
```

To get updates later, run `/plugin marketplace update roblox-skills`.

### Any agent (install script)

```bash
git clone https://github.com/EL4CTEO/roblox-skills.git
cd roblox-skills

# Into the current project, for Codex / Gemini CLI / Copilot / OpenCode / Cursor (.agents/skills):
./scripts/install.sh --project /path/to/your/game

# For Claude Code, available in all your projects (~/.claude/skills):
./scripts/install.sh --agent claude --global

# Only some skills, symlinked so that `git pull` updates them:
./scripts/install.sh --agent opencode --global --link roblox-luau roblox-security roblox-data-stores
```

On Windows, run `.\scripts\install.ps1 -Agent claude -Global`.

| Agent | Project directory | Global directory | `--agent` |
| --- | --- | --- | --- |
| Codex, Gemini CLI, GitHub Copilot, OpenCode, Cursor | `.agents/skills/` | `~/.agents/skills/` | `agents` (default) |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` | `claude` |
| OpenCode | `.opencode/skills/` | `~/.config/opencode/skills/` | `opencode` |
| Gemini CLI | `.gemini/skills/` | `~/.gemini/skills/` | `gemini` |
| GitHub Copilot | `.github/skills/` | `~/.copilot/skills/` | `copilot` |

Some agents read several of these directories. OpenCode and Copilot, for example, also read
`.claude/skills`. For those agents, install into only one directory so you don't get duplicate skills.
You can also copy the `skills/*` folders by hand, or use any skills manager that installs from a GitHub
repository's `skills/` directory.

### Roblox Studio Assistant

```bash
python3 scripts/build-assistant.py        # writes dist/assistant/<skill>.md
```

This build inlines each skill's references, because Assistant skills are single documents. In Studio,
open **Assistant → … → Assistant Settings → Skills → Add** and paste a file. Each CI run also uploads
these bundles as a build artifact.

## Pair with the Studio MCP server

Agents do their best Roblox work when they can **verify** changes. Studio has a built-in MCP server:
enable it under **Assistant → Manage MCP Servers**, then connect your agent. The
[roblox-studio-mcp](skills/roblox-studio-mcp/SKILL.md) skill covers the setup for each client and a
safe explore → edit → playtest → check-output loop.

## Example prompts

- "Add a shop where players buy swords with coins, and make it exploit-proof."
- "Save player inventory and coins with session locking, and migrate from my old DataStore format."
- "Make the HUD work on phones and gamepads."
- "Why does my game lag after 30 minutes? Here's a MicroProfiler dump."
- "Set up Rojo, Wally, and CI with type checking for this project."
- "Review `ServerScriptService` for exploits and deprecated APIs."
- "Convert this BodyVelocity dash into modern constraints and validate it on the server."

## Quality checks

```bash
./scripts/setup-tools.sh          # downloads luau-lsp, StyLua, and Roblox type definitions into .tools/
python3 scripts/validate.py       # frontmatter, links, Luau type checks, formatting, deprecated APIs
```

The validator enforces these rules:

- Every skill follows the Agent Skills spec and Roblox Assistant's naming rules.
- Every `SKILL.md` stays under 500 lines.
- Every link resolves, and every reference file is linked from somewhere.
- Every ` ```luau ` block type-checks against the Roblox API. Only a deliberately wrong "don't do this"
  example may opt out, with ` ```luau nocheck `.

## Sources and currency

The content is checked against Roblox's official [creator documentation](https://github.com/Roblox/creator-docs)
and engine API reference (Studio 0.740, September 2026), the [Luau documentation](https://luau.org),
and the current releases of community tools (Rojo 7.7, Rokit 1.2, Wally 0.3, Lune 0.10, luau-lsp 1.70,
StyLua 2.5, selene 0.31, Jest Lua 3.10, ProfileStore 1.0). Features that are still in beta, such as
server authority, the Character Controller Library, and `InputActionLabel`, are marked as beta in the
skills.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Issues and PRs are welcome, especially for corrections when
Roblox changes an API.

## License

[MIT](LICENSE). Roblox, Roblox Studio, and Luau are trademarks of Roblox Corporation. This project is
not affiliated with or endorsed by Roblox.
