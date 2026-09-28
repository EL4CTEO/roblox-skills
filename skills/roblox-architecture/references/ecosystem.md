# Roblox open-source ecosystem (2026)

Guidance, not endorsements. **Always check the project's repository for its current status and API
before adding it** — several popular libraries were archived or rewritten recently. If a project already
uses a library, follow it instead of introducing an alternative. Install with Wally or pesde (see
`roblox-tooling`).

## Frameworks

- **None (recommended)** — a single entry script per side that requires service/controller modules
  (see SKILL.md). Fully typed, no magic.
- **Knit** — archived by its author in July 2024. Don't start new projects on it; maintain existing ones.
- **Flamework** — decorator-based framework for roblox-ts projects.

## Utilities

| Need | Libraries |
| --- | --- |
| Signals | `sleitnick/signal`, GoodSignal, LemonSignal |
| Cleanup | Trove (`sleitnick/trove`), Janitor, Maid |
| Promises | `evaera/promise` (Promise-based async; optional — plain `task` + `pcall` is fine) |
| Tables/functional | Sift, Dash |

## Networking (buffer-packed, schema-driven)

- **Zap** and **Blink** — IDL compilers: you write a schema, they generate typed, validated,
  buffer-serialized remote code for client and server. Both have had rewrites/forks; check which
  branch/fork is maintained.
- **ByteNet**, **Packet** — runtime (non-codegen) buffer networking libraries.
- Plain `RemoteEvent`s are fine for most games; adopt these when bandwidth or remote CPU shows up in profiling.

## Data

- **ProfileStore** (loleris) — session-locked player data, successor to ProfileService; uses
  MessagingService to resolve lock conflicts quickly. The default choice for player data.
- **Lapis** — alternative DataStore wrapper with session locking and migrations.
- **Replica** (loleris) — replicate server state tables to clients.
- DataStore2 — legacy; don't use for new work.

## UI

- **React** (`jsdotlua/react` + `jsdotlua/react-roblox`, the Roblox port of React 17) — hooks, large apps.
- **Fusion** — reactive state + declarative instances.
- **Vide** — lightweight reactive UI library.
- Plain instances + Studio's UI editor + StyleSheets for simple UIs.

## ECS

- **jecs** — fast archetype ECS with relationships and a typed Luau API.
- **Matter** — earlier ECS with a debugger; less active.

## Testing / tooling libs

- **Jest Lua** (`jsdotlua/jest`) — Jest port; the modern test framework. TestEZ is legacy.
- See `roblox-testing` and `roblox-tooling`.

## roblox-ts

TypeScript → Luau compiler (`roblox-ts`, npm `@rbxts/*` packages). If a project has `tsconfig.json` and
`@rbxts/types`, write TypeScript, not Luau, and use `@rbxts/services` imports.
