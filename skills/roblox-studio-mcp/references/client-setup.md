# Connecting MCP clients to Roblox Studio

Server command:
- macOS: `/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP`
- Windows: `cmd.exe` with args `/c %LOCALAPPDATA%\Roblox\mcp.bat`

Enable it first in Studio: **Assistant → … → Manage MCP Servers → Enable Studio as MCP server**.
Client config formats change over time; if one below doesn't load, check that client's MCP docs.

## Claude Code

```bash
claude mcp add Roblox_Studio -- /Applications/RobloxStudio.app/Contents/MacOS/StudioMCP
# Windows (PowerShell/cmd):
claude mcp add Roblox_Studio -- cmd.exe /c "%LOCALAPPDATA%\Roblox\mcp.bat"
```

Or project-scoped `.mcp.json` at the repo root:

```json
{
  "mcpServers": {
    "Roblox_Studio": {
      "command": "/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP"
    }
  }
}
```

## Claude Desktop / Cursor / VS Code (mcp.json-style)

```json
{
  "mcpServers": {
    "Roblox_Studio": {
      "command": "cmd.exe",
      "args": ["/c", "%LOCALAPPDATA%\\Roblox\\mcp.bat"]
    }
  }
}
```

(VS Code's `.vscode/mcp.json` uses a top-level `"servers"` key instead of `"mcpServers"`.)

## OpenAI Codex CLI (`~/.codex/config.toml`)

```toml
[mcp_servers.roblox_studio]
command = "/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP"
```

## OpenCode (`opencode.json`)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "roblox_studio": {
      "type": "local",
      "command": ["/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP"],
      "enabled": true
    }
  }
}
```

## Gemini CLI (`~/.gemini/settings.json`)

```json
{
  "mcpServers": {
    "Roblox_Studio": { "command": "/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP" }
  }
}
```

## Troubleshooting

- Restart both Studio and the client after changing config.
- Verify the binary path exists (Studio updates can move it; re-copy from **Manage MCP Servers**).
- JSON syntax errors (missing commas) silently prevent loading.
- Remote/cloud agents (running on another machine or in a container) can't reach a local Studio over
  stdio; run the agent on the machine where Studio runs.
- Older setups used the standalone open-source `Roblox/studio-rust-mcp-server` + plugin; the built-in
  server supersedes it.
