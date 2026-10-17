# Changelog

## 1.1.1 — 2026-10-17

Updated for Roblox releases from mid-September to October 17, 2026 (Studio 0.743).

- **Fixes**: server authority is fully released (no more "rolling out"), and the camera now syncs through
  `Player:GetCameraState()`; `ClipsDescendants` clips rotated UI by default; Device Emulator → Device Simulator.
- **Physics**: `BasePart:BindToCollisionSummaries` for impact point, normal, and speed; `CollisionFidelity.Tunable`.
- **Streaming**: `Player.FrustumStreaming` for scopes, racing, and free cameras.
- **Monetization**: `MarketplaceService:OpenShop`, selling items outside the game, refund handling, age
  check API (`PromptAgeCheck`, `AgeChecked`), and the US 18+ DevEx rate.
- **Open Cloud**: Transaction Refunded webhook details, legacy web API rate-limit cuts, new thumbnail error format.
- **Data stores**: Roblox-native Friends and Global leaderboards.
- **Audio**: Acoustic Simulation (fully released) and text-to-speech auto-translation.
- **Chat, analytics, building**: custom Quick Words, Early Harm Detection, Player Support reports, early
  testers, the new discovery measurement, and EditableMesh batch APIs.

## 1.1.0 — 2026-09-28

- Support for many more agents. `install.sh` and `install.ps1` now read their targets from
  `scripts/agents.tsv` and add Windsurf, Roo Code, Kiro, JetBrains Junie, Goose, Qwen Code, Continue,
  Crush, Trae, Augment, OpenHands, Devin, Mistral Vibe, Qoder, CodeBuddy, Tabnine, Rovo Dev, iFlow,
  Pi, Antigravity, Amp, Kilo Code, Factory Droid, and Cursor's global folder. Run
  `--list-agents` / `-ListAgents` to see them.
- README and the new `docs/agents.md` document `npx skills add EL4CTEO/roblox-skills`, which installs
  into 70+ agents.
- `install.ps1`: skill names now work without `-Agent` (they were bound to the wrong parameter), and
  `-Agent a,b` works when the script is run with `pwsh -File`.
- `validate.py` checks `scripts/agents.tsv` and that `docs/agents.md` lists every agent.

## 1.0.0 — 2026-09-28

- Initial release: 23 skills covering Luau, architecture, networking, security, data stores,
  monetization, UI, input, physics, characters and animation, NPC AI, performance, tooling, testing,
  Open Cloud, Studio MCP, audio, text chat, teleports and matchmaking, analytics and live ops, world
  building, game systems, and code review.
- Verified against Roblox creator docs and the engine API reference (Studio 0.740).
- `scripts/validate.py` checks the spec, links, and formatting, type-checks every Luau example with
  luau-lsp, and scans for deprecated APIs.
- Claude Code plugin marketplace, cross-agent installers (`install.sh` / `install.ps1`), and a Roblox
  Studio Assistant bundle builder.
