# Contributing

Thanks for helping keep these skills accurate. Roblox changes fast, so corrections are the most
valuable contribution.

## Ground rules

1. **Verify against a primary source.** Use Roblox's creator docs and engine API reference
   (`github.com/Roblox/creator-docs`, `create.roblox.com/docs`), luau.org, or the tool's own repository.
   Don't rely on memory, forum posts, or older tutorials.
2. **Keep `SKILL.md` lean.** Put what an agent needs on most tasks in `SKILL.md`, and put deep detail in
   `references/*.md`, linked from `SKILL.md`. Stay under 500 lines.
3. **Write descriptions for triggering.** A description says what the skill covers and when to use it,
   in one line under about 450 characters. Include the keywords users actually type. Don't use `": "`
   inside it (that's invalid YAML unless quoted).
4. **Make code real.** Every ` ```luau ` block must type-check in strict mode against the current Roblox
   API and must be formatted with StyLua. Use ` ```luau nocheck ` only for deliberately wrong examples.
   Tag every other code fence with its language (`bash`, `json`, `toml`, `text`, ...).
5. **Prefer current APIs.** Use the `*Async` variants, `task.*`, mover constraints, `Raycast`,
   `TextChatService`, and so on. If you mention a deprecated API, name its replacement.
6. **Mark beta features.** Say that a feature is in beta and tell readers to check its status.

## Workflow

```bash
./scripts/setup-tools.sh            # once: luau-lsp, StyLua, Roblox definitions → .tools/
python3 scripts/validate.py         # must pass with 0 errors
python3 scripts/validate.py roblox-ui          # check one skill
python3 scripts/validate.py --fix-format       # reformat luau blocks with StyLua
claude plugin validate .            # if you have Claude Code: check the plugin manifests
```

## Adding a skill

1. Create `skills/roblox-<topic>/SKILL.md` with `name` (it must match the folder) and `description`.
2. Add a row to the README table, and list the skill under "Related skills" in neighboring skills.
3. Run the validator.

## Releasing

Bump `version` in `.claude-plugin/plugin.json` and add a `## x.y.z — date` entry to `CHANGELOG.md`.
Then push a `vX.Y.Z` tag, or run the **Release** workflow manually with that tag. It validates the
skills, builds `roblox-skills.zip` and the Studio Assistant bundle, and publishes the GitHub release.
