# Instructions for AI agents working in this repository

This repository *is* a skills collection. It is not a Roblox game.

- Skills live in `skills/<name>/SKILL.md`, with optional `references/*.md`. Follow `CONTRIBUTING.md`.
- Before you finish any change, run `python3 scripts/validate.py`. It must report 0 errors. If `.tools/`
  is missing, run `./scripts/setup-tools.sh` first.
- Treat the Roblox engine API reference (`Roblox/creator-docs`, `content/en-us/reference/engine`) as
  the source of truth for API names, deprecations, and limits. Never add an API you haven't verified.
- Keep every `SKILL.md` concise: defaults, decision tables, and short verified examples. Move long
  material into `references/`.
- Luau style: tabs, double quotes, `--!strict`, services via `game:GetService`, `task.*`, and current
  `*Async` APIs. StyLua config is in `stylua.toml`.
- Don't commit `.tools/`, `.check/`, or `dist/`.
