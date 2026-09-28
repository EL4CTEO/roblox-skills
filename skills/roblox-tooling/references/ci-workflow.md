# GitHub Actions CI for a Rojo project

Assumes `rokit.toml` (with rojo, wally, stylua, selene, luau-lsp), `default.project.json`, `wally.toml`,
`selene.toml`, `stylua.toml`, and optionally `.luaurc`.

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main]
  pull_request:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Rokit and tools
        run: |
          curl -sSf https://raw.githubusercontent.com/rojo-rbx/rokit/main/scripts/install.sh | bash
          echo "$HOME/.rokit/bin" >> "$GITHUB_PATH"
          "$HOME/.rokit/bin/rokit" install --no-trust-check
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Install packages
        run: |
          wally install
          rojo sourcemap default.project.json -o sourcemap.json

      - name: Format
        run: stylua --check src

      - name: Lint
        run: selene src

      - name: Type check
        run: |
          curl -fsSL -o globalTypes.d.luau \
            https://raw.githubusercontent.com/JohnnyMorganz/luau-lsp/main/scripts/globalTypes.d.luau
          luau-lsp analyze \
            --definitions=@roblox=globalTypes.d.luau \
            --sourcemap=sourcemap.json \
            --base-luaurc=.luaurc \
            --ignore="Packages/**" \
            src

      - name: Build place
        run: rojo build default.project.json -o build.rbxl

      - uses: actions/upload-artifact@v4
        with:
          name: place
          path: build.rbxl
```

Notes:
- Rokit's installer path and flags may change between versions; check its README if the step fails.
- Cache `~/.rokit` and `Packages/` with `actions/cache` keyed on `rokit.toml`/`wally.lock` for speed.

## Publishing with Open Cloud

Create an API key (Creator Dashboard → Open Cloud → API Keys) with the **universe-places** permission (write) for the
target universe, store it as a repository secret `ROBLOX_API_KEY`, then:

```yaml
  publish:
    needs: check
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: place
      - name: Publish place version
        run: |
          curl --fail -X POST \
            "https://apis.roblox.com/universes/v1/${{ vars.UNIVERSE_ID }}/places/${{ vars.PLACE_ID }}/versions?versionType=Published" \
            -H "x-api-key: ${{ secrets.ROBLOX_API_KEY }}" \
            -H "Content-Type: application/octet-stream" \
            --data-binary @build.rbxl
```

Use `versionType=Saved` to upload without publishing (e.g. to a staging place). Publish to a separate
**staging universe** first and run tests there (see `roblox-testing` for running tests in the cloud
with Open Cloud Luau execution).
