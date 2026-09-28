<#
.SYNOPSIS
  Install Roblox skills for AI coding agents (Windows PowerShell).

.EXAMPLE
  .\scripts\install.ps1 -Agent claude -Global
  .\scripts\install.ps1 -Agent agents -Project C:\games\my-obby roblox-luau roblox-security
#>
param(
    [ValidateSet("agents", "claude", "opencode", "gemini", "copilot")]
    [string[]]$Agent = @("agents"),
    [switch]$Global,
    [string]$Project = (Get-Location).Path,
    [switch]$Force,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Skills
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$skillsDir = Join-Path $root "skills"

if (-not $Skills -or $Skills.Count -eq 0) {
    $Skills = Get-ChildItem -Directory $skillsDir | ForEach-Object { $_.Name }
}
foreach ($name in $Skills) {
    if (-not (Test-Path (Join-Path $skillsDir "$name\SKILL.md"))) {
        throw "Unknown skill: $name"
    }
}

function Get-TargetDir([string]$name) {
    if ($Global) {
        switch ($name) {
            "agents"   { return Join-Path $HOME ".agents\skills" }
            "claude"   { return Join-Path $HOME ".claude\skills" }
            "opencode" { return Join-Path $HOME ".config\opencode\skills" }
            "gemini"   { return Join-Path $HOME ".gemini\skills" }
            "copilot"  { return Join-Path $HOME ".copilot\skills" }
        }
    }
    switch ($name) {
        "agents"   { return Join-Path $Project ".agents\skills" }
        "claude"   { return Join-Path $Project ".claude\skills" }
        "opencode" { return Join-Path $Project ".opencode\skills" }
        "gemini"   { return Join-Path $Project ".gemini\skills" }
        "copilot"  { return Join-Path $Project ".github\skills" }
    }
}

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
