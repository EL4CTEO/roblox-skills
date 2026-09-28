<#
.SYNOPSIS
  Install Roblox skills for AI coding agents (Windows PowerShell).

.DESCRIPTION
  -Agent defaults to "agents" (.agents\skills, the shared folder read by Codex, Cursor, Gemini CLI,
  Copilot, OpenCode, Amp, Cline and more). Run with -ListAgents to see every supported agent.

.EXAMPLE
  .\scripts\install.ps1 -Agent claude -Global
  .\scripts\install.ps1 -Agent agents -Project C:\games\my-obby roblox-luau roblox-security
  .\scripts\install.ps1 -Agent agents, windsurf -Global
#>
[CmdletBinding(PositionalBinding = $false)]
param(
    [string[]]$Agent = @("agents"),
    [switch]$Global,
    [string]$Project = (Get-Location).Path,
    [switch]$Force,
    [switch]$ListAgents,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Skills
)

$ErrorActionPreference = "Stop"
$Agent = @($Agent | ForEach-Object { $_ -split "," } | Where-Object { $_ })
$root = Split-Path -Parent $PSScriptRoot
$skillsDir = Join-Path $root "skills"

# id, aliases, project dir, global dir, tools (see scripts/agents.tsv)
$agentTable = Get-Content (Join-Path $root "scripts\agents.tsv") |
    Where-Object { $_ -and -not $_.StartsWith("#") } |
    ForEach-Object {
        $c = $_ -split "`t"
        [pscustomobject]@{ Id = $c[0]; Aliases = $c[1] -split ","; Project = $c[2]; Global = $c[3]; Tools = $c[4] }
    }

if ($ListAgents) {
    $agentTable | Format-Table Id, Project, Global, Tools -AutoSize | Out-String -Width 200 | Write-Host
    exit 0
}

if (-not $Skills -or $Skills.Count -eq 0) {
    $Skills = Get-ChildItem -Directory $skillsDir | ForEach-Object { $_.Name }
}
foreach ($name in $Skills) {
    if (-not (Test-Path (Join-Path $skillsDir "$name\SKILL.md"))) {
        throw "Unknown skill: $name"
    }
}

$sep = [IO.Path]::DirectorySeparatorChar

function Get-TargetDir([string]$name) {
    $row = $agentTable | Where-Object { $_.Id -eq $name -or $_.Aliases -contains $name } | Select-Object -First 1
    if (-not $row) { throw "Unknown agent: $name (run with -ListAgents)" }
    if (-not $Global) { return Join-Path $Project ($row.Project -replace '/', $sep) }
    $configHome = if ($env:XDG_CONFIG_HOME) { $env:XDG_CONFIG_HOME } else { Join-Path $HOME ".config" }
    $path = ($row.Global -replace '^~', $HOME) -replace '^\$CONFIG', $configHome
    return $path -replace '/', $sep
}

foreach ($a in $Agent) { Get-TargetDir $a | Out-Null }

foreach ($a in $Agent) {
    $dest = Get-TargetDir $a
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    $installed = 0; $skipped = 0
    foreach ($name in $Skills) {
        $out = Join-Path $dest $name
        if (Test-Path $out) {
            if (-not $Force) { $skipped++; continue }
            Remove-Item -Recurse -Force $out
        }
        Copy-Item -Recurse (Join-Path $skillsDir $name) $out
        $installed++
    }
    $note = if ($skipped) { " ($skipped already present; use -Force to replace)" } else { "" }
    Write-Host "${a}: installed $installed skill(s) into $dest$note"
}

Write-Host ""
Write-Host "Done. Restart your agent so it discovers the skills."
Write-Host "Claude Code: /plugin marketplace add EL4CTEO/roblox-skills, then /plugin install roblox-skills@roblox-skills"
