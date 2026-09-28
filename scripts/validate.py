#!/usr/bin/env python3
"""Validate every skill in skills/.

Checks
  1. Frontmatter follows the Agent Skills spec (https://agentskills.io/specification)
     and Roblox Assistant's rules (single-line fields, no reserved `rbx-` prefix).
  2. SKILL.md stays small (progressive disclosure) and every relative link resolves.
     Every file in references/ must be linked from its SKILL.md (no orphans).
  3. Every ```luau code block:
       - is type-checked by luau-lsp (new type solver) against the current Roblox API definitions in strict mode.
         Blocks that declare `--!strict` themselves must be completely clean. Other blocks only
         fail on API-validity errors: syntax errors, unknown globals/types, members that do not
         exist on Roblox classes, and deprecated APIs.
       - is formatted with StyLua (stylua.toml).
       - does not use APIs that Roblox has deprecated (curated list below, from the engine API reference).
     Use ```luau nocheck only for deliberately-wrong examples ("don't do this").
  4. Code fences must declare a language; Roblox code must be tagged `luau`, not `lua`.
  5. scripts/agents.tsv (read by the installers) is well formed and docs/agents.md lists every agent.

Usage: python3 scripts/validate.py [--no-luau] [--fix-format]
Tools: run scripts/setup-tools.sh once (installs into .tools/), or set LUAU_LSP, STYLUA, ROBLOX_DEFS.
"""

from __future__ import annotations

import argparse
import difflib
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
CHECK_DIR = ROOT / ".check"

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
MAX_SKILL_LINES = 500
MAX_DESCRIPTION = 1024

# Deprecated Roblox APIs (source: creator-docs engine reference, `Deprecated` tags) -> replacement.
# Matched as regexes against luau code blocks (not against prose, where we mention them on purpose).
DEPRECATED = [
    (r"(?<![\w.:])wait\s*\(", "task.wait()"),
    (r"(?<![\w.:])spawn\s*\(", "task.spawn()"),
    (r"(?<![\w.:])delay\s*\(", "task.delay()"),
    (r"\bypcall\s*\(", "pcall()"),
    (r"\btable\.(getn|foreach|foreachi)\b", "# / for-in loops"),
    (r"\b(getfenv|setfenv)\s*\(", "nothing (disables optimizations)"),
    (r":FindPartOnRay\w*\s*\(", "WorldRoot:Raycast() + RaycastParams"),
    (r":FindPartsInRegion3\w*\s*\(|:IsRegion3Empty\w*\s*\(", "GetPartBoundsInBox() + OverlapParams"),
    (r":SetPrimaryPartCFrame\s*\(", "Model:PivotTo()"),
    (r":GetPrimaryPartCFrame\s*\(", "Model:GetPivot()"),
    (r"\bHumanoid:LoadAnimation\b|\bhumanoid:LoadAnimation\b", "Animator:LoadAnimation()"),
    (r":LoadCharacter\s*\(", "Player:LoadCharacterAsync()"),
    (r":LoadCharacterWithHumanoidDescription\s*\(", "LoadCharacterWithHumanoidDescriptionAsync()"),
    (r":GetProductInfo\s*\(", "MarketplaceService:GetProductInfoAsync()"),
    (r":PlayerOwnsAsset\s*\(", "PlayerOwnsAssetAsync()"),
    (r":AwardBadge\s*\(", "BadgeService:AwardBadgeAsync()"),
    (r":UserHasBadge\s*\(", "BadgeService:UserHasBadgeAsync()"),
    (r":GetRankInGroup(Async)?\s*\(|:GetRoleInGroup(Async)?\s*\(", "GroupService:GetRolesInGroupAsync()"),
    (r":IsInGroup\s*\(", "Player:IsInGroupAsync()"),
    (r":IsFriendsWith\s*\(", "Player:IsFriendsWithAsync()"),
    (r":GetFriendsOnline\s*\(", "Player:GetFriendsOnlineAsync()"),
    (r":ApplyDescription\s*\(", "Humanoid:ApplyDescriptionAsync()"),
    (r":ApplyDescriptionReset\s*\(", "Humanoid:ApplyDescriptionResetAsync()"),
    (r":PlayEmote\s*\(", "Humanoid:PlayEmoteAsync()"),
    (r":GetHumanoidDescriptionFromUserId\s*\(", "GetHumanoidDescriptionFromUserIdAsync()"),
    (r":CreateHumanoidModelFrom(Description|UserId)\s*\(", "CreateHumanoidModelFrom...Async()"),
    (r":GetTranslatorForPlayer\s*\(", "GetTranslatorForPlayerAsync()"),
    (r":ReserveServer\s*\(", "TeleportService:ReserveServerAsync()"),
    (r":TeleportPartyAsync|:TeleportToPlaceInstance|:TeleportToPrivateServer|:TeleportToSpawnByName",
     "TeleportService:TeleportAsync()"),
    (r":PromptPremiumPurchase\s*\(", "PromptRobloxSubscriptionPurchase()"),
    (r":FireCustomEvent|:FireInGameEconomyEvent|:FirePlayerProgressionEvent",
     "AnalyticsService:LogCustomEvent/LogEconomyEvent/LogProgressionEvent"),
    (r"\.(Velocity|RotVelocity)\s*=", "AssemblyLinearVelocity / AssemblyAngularVelocity"),
    (r"Instance\.new\(\s*\"(BodyVelocity|BodyPosition|BodyGyro|BodyForce|BodyThrust|BodyAngularVelocity|RocketPropulsion)\"",
     "mover constraints (LinearVelocity, AlignPosition, AlignOrientation, VectorForce, AngularVelocity, LineForce)"),
    (r":SetPartCollisionGroup|:CreateCollisionGroup|:GetCollisionGroupId", "BasePart.CollisionGroup / RegisterCollisionGroup"),
    # Superseded (deprecation message in the API reference, not yet tagged Deprecated):
    (r"PhysicsService:(RegisterCollisionGroup|CollisionGroupSetCollidable|CollisionGroupsAreCollidable|GetRegisteredCollisionGroups|IsCollisionGroupRegistered|UnregisterCollisionGroup|RenameCollisionGroup|GetMaxCollisionGroups)",
     "the same method on workspace (WorldRoot)"),
    (r"\.MembershipType\b", "Player.HasRobloxSubscription"),
    (r":FindPathAsync\s*\(", "PathfindingService:CreatePath() + Path:ComputeAsync()"),
    (r"Lighting\.Technology\b|\.Technology\s*=", "Lighting.LightingStyle / PrioritizeLightingQuality"),
    (r"\.KeyframeReached\b", "AnimationTrack:GetMarkerReachedSignal()"),
    (r":IsTenFootInterface\s*\(", "GuiService.ViewportDisplaySize"),
    (r"\.(Steer|Throttle)\b(?!Float)", "VehicleSeat.SteerFloat / ThrottleFloat"),
    (r"UserInputService\.VREnabled", "VRService.VREnabled"),
    (r"TeleportService:Teleport\s*\(", "TeleportService:TeleportAsync() on the server"),
    (r":SetRoll\s*\(|:GetRoll\s*\(", "Camera.CFrame"),
    (r"\.PrimaryAxisOnly\b", "AlignOrientation.AlignType"),
    (r":Tween(Position|Size|SizeAndPosition)\s*\(", "TweenService:Create()"),
    (r"\.Pitch\s*=", "Sound.PlaybackSpeed"),
    (r":GetChatForUserAsync\s*\(", "TextChatService channels (this now returns an empty string)"),
    (r"ContentProvider:Preload\s*\(", "ContentProvider:PreloadAsync()"),
    (r":GetModelCFrame\s*\(|:GetModelSize\s*\(", "Model:GetPivot() / Model:GetExtentsSize()"),
    (r"CollectionService:GetCollection\b", "CollectionService:GetTagged()"),
    (r"Instance\.new\(\s*\"(Hint|Message|HopperBin|Hat|Skin|FloorWire|Glue|Snap|ManualWeld)\"", "modern equivalents (TextLabel, Tool, Accessory, WeldConstraint...)"),
    (r"\.(VIPServerId|VIPServerOwnerId)\b", "game.PrivateServerId / PrivateServerOwnerId"),
    (r"\.DataReady\b|:WaitForDataReady|:Save(Number|String|Boolean|Instance)\s*\(|:Load(Number|String|Boolean|Instance)\s*\(", "DataStoreService"),
    (r"\bOnUpdate\s*\(", "MessagingService"),
    (r"\bGetService\(\s*\"OpenCloudService\"\s*\)", "HttpService"),
    (r":Remove\s*\(\s*\)", "Instance:Destroy()"),
    (r"\bGetService\(\s*\"Chat\"\s*\)", "TextChatService"),
    (r"\.Draggable\s*=", "UIDragDetector"),
    (r"\bworkspace\.FilteringEnabled\b", "nothing (always on)"),
    (r"\bmouse\.KeyDown\b|\bMouse\.KeyDown\b", "UserInputService / Input Action System"),
    (r":Interpolate\s*\(", "TweenService"),
    (r"\bRegion3\.new\b", "GetPartBoundsInBox() + OverlapParams"),
    (r"\bRay\.new\b", "WorldRoot:Raycast(origin, direction, params)"),
]

# luau-lsp diagnostics kept for blocks that don't opt into full strict.
API_ERROR_PATTERNS = [
    "SyntaxError",
    "not found in external type",
    "DeprecatedApi",
    "Unknown global",
    "UnknownGlobal",
    "Unknown type",
    "is not a valid member",
]
# Never reported (fine in illustrative snippets).
IGNORED_PATTERNS = ["LocalUnused", "FunctionUnused", "ImportUnused", "Unknown require", "LocalShadow"]


@dataclass
class Block:
    md: Path
    start: int  # 1-based line of the first code line in the markdown file
    info: str
    code: str


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checked_blocks: int = 0
    skipped_blocks: int = 0

    def err(self, path: Path, line: int, msg: str) -> None:
        self.errors.append(f"{path.relative_to(ROOT)}:{line}: {msg}")

    def warn(self, path: Path, line: int, msg: str) -> None:
        self.warnings.append(f"{path.relative_to(ROOT)}:{line}: {msg}")


def parse_frontmatter(text: str) -> tuple[dict[str, str], int] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    raw = text[4:end]
    fields: dict[str, str] = {}
    current = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        if line.startswith((" ", "\t")) and current:
            fields[current] += "\n" + line.strip()  # nested (metadata) or multi-line value
            continue
        key, sep, value = line.partition(":")
        if not sep:
            return None
        current = key.strip()
        fields[current] = value.strip()
    body_start = text[: end + 5].count("\n") + 1
    return fields, body_start


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def check_skill(skill_dir: Path, report: Report) -> list[Block]:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        report.err(skill_dir, 0, "missing SKILL.md")
        return []
    text = skill_md.read_text(encoding="utf-8")
    parsed = parse_frontmatter(text)
    if parsed is None:
        report.err(skill_md, 1, "missing or malformed YAML frontmatter")
        return []
    fields, _ = parsed
    try:
        import yaml  # optional: strict YAML check (e.g. unquoted ": " breaks many parsers)

        yaml.safe_load(text[4 : text.find("\n---\n", 4)])
    except ImportError:
        pass
    except Exception as exc:  # noqa: BLE001 - report any YAML error
        report.err(skill_md, 1, f"frontmatter is not valid YAML: {exc}".splitlines()[0])
    for key, value in fields.items():
        if ": " in value and not value.startswith(("'", '"')):
            report.err(skill_md, 1, f"unquoted ': ' in '{key}' is invalid YAML; rephrase or quote it")

    for key in fields:
        if key not in ALLOWED_KEYS:
            report.err(skill_md, 1, f"unknown frontmatter key '{key}'")
    name = unquote(fields.get("name", ""))
    desc = unquote(fields.get("description", ""))
    if not name:
        report.err(skill_md, 1, "missing 'name'")
    elif not NAME_RE.match(name) or len(name) > 64:
        report.err(skill_md, 1, f"invalid name '{name}' (lowercase letters, digits, single hyphens, <=64 chars)")
    elif name != skill_dir.name:
        report.err(skill_md, 1, f"name '{name}' must match directory '{skill_dir.name}'")
    elif name.startswith("rbx-"):
        report.err(skill_md, 1, "the 'rbx-' prefix is reserved for Roblox-authored skills")
    if not desc:
        report.err(skill_md, 1, "missing 'description'")
    else:
        if "\n" in desc:
            report.err(skill_md, 1, "description must be a single line")
        if len(desc) > MAX_DESCRIPTION:
            report.err(skill_md, 1, f"description is {len(desc)} chars (max {MAX_DESCRIPTION})")
        if "use when" not in desc.lower() and "use for" not in desc.lower():
            report.warn(skill_md, 1, "description should say when to use the skill ('Use when ...')")

    lines = text.count("\n") + 1
    if lines > MAX_SKILL_LINES:
        report.err(skill_md, lines, f"SKILL.md has {lines} lines (max {MAX_SKILL_LINES}); move detail to references/")

    blocks: list[Block] = []
    md_files = sorted(skill_dir.rglob("*.md"))
    linked: set[Path] = set()
    for md in md_files:
        blocks += check_markdown(md, report, linked)

    refs = skill_dir / "references"
    if refs.is_dir():
        for f in sorted(refs.rglob("*")):
            if f.is_file() and f.resolve() not in linked:
                report.err(f, 1, "orphan file: not linked from any markdown file in the skill")
    return blocks


LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")


def check_markdown(md: Path, report: Report, linked: set[Path]) -> list[Block]:
    text = md.read_text(encoding="utf-8")
    blocks: list[Block] = []
    lines = text.splitlines()
    in_fence = False
    fence = ""
    info = ""
    start = 0
    buf: list[str] = []
    for i, line in enumerate(lines, 1):
        m = FENCE_RE.match(line)
        if not in_fence and m:
            in_fence, fence, info, start, buf = True, m.group(2), m.group(3).strip(), i + 1, []
            lang = info.split()[0] if info else ""
            if not lang:
                report.err(md, i, "code fence without a language (use luau, bash, json, text, ...)")
            elif lang == "lua":
                report.err(md, i, "tag Roblox code as ```luau, not ```lua")
            continue
        if in_fence:
            if m and m.group(2).startswith(fence[0]) and len(m.group(2)) >= len(fence) and not m.group(3).strip():
                in_fence = False
                if info.split()[:1] == ["luau"]:
                    blocks.append(Block(md, start, info, "\n".join(buf) + "\n"))
            else:
                buf.append(line)
            continue
        for target in LINK_RE.findall(line):
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                continue
            path = (md.parent / target.split("#")[0]).resolve()
            if not path.exists():
                report.err(md, i, f"broken link: {target}")
            else:
                linked.add(path)
    if in_fence:
        report.err(md, start - 1, "unclosed code fence")
    return blocks


def check_deprecated(block: Block, report: Report) -> None:
    if "nocheck" in block.info.split()[1:]:
        return
    for offset, line in enumerate(block.code.splitlines()):
        code = re.sub(r"--.*$", "", line)
        no_strings = re.sub(r"\"[^\"]*\"|'[^']*'|`[^`]*`", '""', code)
        for pattern, replacement in DEPRECATED:
            # Patterns that look inside string literals (GetService("..."), Instance.new("...")) see the raw line.
            target = code if '\\"' in pattern else no_strings
            if re.search(pattern, target):
                report.err(block.md, block.start + offset, f"deprecated API; use {replacement}")


def tool(env: str, name: str) -> str | None:
    if os.environ.get(env):
        return os.environ[env]
    local = ROOT / ".tools" / name
    if local.exists():
        return str(local)
    return shutil.which(name)


HOT_COMMENT_RE = re.compile(r"^--!\w+")


def prepare(block: Block) -> tuple[str, bool, int, int]:
    """Return (source, full_strict, shim_line, hot) with `--!strict` enforced and a `script` shim inserted.

    `script` is typed `any` so snippets can use script.Parent.X without a Rojo sourcemap.
    """
    lines = block.code.splitlines()
    full = any(l.strip() == "--!strict" for l in lines)
    hot = 0
    while hot < len(lines) and HOT_COMMENT_RE.match(lines[hot].strip()):
        hot += 1
    header = [l for l in lines[:hot] if l.strip() not in ("--!strict", "--!nonstrict", "--!nocheck")]
    out = ["--!strict", *header, "local script: any = script", *lines[hot:]]
    shim_line = 2 + len(header)
    return "\n".join(out) + "\n", full, shim_line, hot


DIAG_RE = re.compile(r"^(.*?)\((\d+),(\d+)\): (.*)$")
MISSING_KEY_RE = re.compile(r"Key '(\w+)' not found in external type '(\w+)'")
TYPE_DECL_RE = re.compile(r"^declare extern type (\w+)(?: extends (\w+))? with")
MEMBER_RE = re.compile(r"^\s+(?:function\s+)?(\w+)\s*[:(]")


def load_classes(defs: str) -> dict[str, tuple[str | None, set[str]]]:
    """Parse the luau-lsp definitions file into {class: (superclass, members)}."""
    classes: dict[str, tuple[str | None, set[str]]] = {}
    current: set[str] | None = None
    for line in Path(defs).read_text(encoding="utf-8").splitlines():
        m = TYPE_DECL_RE.match(line)
        if m:
            current = set()
            classes[m.group(1)] = (m.group(2), current)
        elif line.startswith("end"):
            current = None
        elif current is not None:
            mm = MEMBER_RE.match(line)
            if mm:
                current.add(mm.group(1))
    return classes


def members_of(classes: dict[str, tuple[str | None, set[str]]], cls: str) -> tuple[bool, set[str]]:
    """Return (is_instance_class, all members including inherited)."""
    members: set[str] = set()
    is_instance = False
    seen = 0
    while cls in classes and seen < 50:
        if cls == "Instance":
            is_instance = True
        parent, own = classes[cls]
        members |= own
        cls = parent or ""
        seen += 1
    return is_instance, members


def missing_key_is_error(msg: str, source_line: str, classes) -> str | None:
    """Unknown `.Child` on an Instance may be a real child (no sourcemap), so only flag clear mistakes."""
    m = MISSING_KEY_RE.search(msg)
    if not m:
        return msg
    key, cls = m.groups()
    is_instance, members = members_of(classes, cls)
    if not is_instance:
        return msg  # datatypes (Vector3, CFrame, ...) have no children
    if re.search(rf":\s*{key}\s*\(", source_line):
        return msg  # method calls can't be children
    close = difflib.get_close_matches(key, members, n=1, cutoff=0.85)
    lower = {mm.lower(): mm for mm in members}
    if key.lower() in lower:
        close = [lower[key.lower()]]
    if close:
        return msg if "Did you mean" in msg else f"{msg} (did you mean '{close[0]}'?)"
    if key[:1].islower():
        return msg  # instance children are PascalCase by convention; lowercase is almost always a typo
    return None


def check_luau(blocks: list[Block], report: Report) -> None:
    lsp = tool("LUAU_LSP", "luau-lsp")
    defs = os.environ.get("ROBLOX_DEFS") or str(ROOT / ".tools" / "globalTypes.d.luau")
    stylua = tool("STYLUA", "stylua")
    if not lsp or not Path(defs).exists():
        report.errors.append("luau-lsp or Roblox definitions not found: run scripts/setup-tools.sh (or pass --no-luau)")
        return

    classes = load_classes(defs)
    if CHECK_DIR.exists():
        shutil.rmtree(CHECK_DIR)
    CHECK_DIR.mkdir()
    meta: dict[str, tuple[Block, bool, int, int]] = {}
    raw_files: dict[str, Block] = {}
    for n, block in enumerate(blocks):
        if "nocheck" in block.info.split()[1:]:
            report.skipped_blocks += 1
            continue
        report.checked_blocks += 1
        src, full, shim_line, hot = prepare(block)
        fname = CHECK_DIR / f"b{n:04d}.luau"
        fname.write_text(src, encoding="utf-8")
        meta[str(fname)] = (block, full, shim_line, hot)
        raw = CHECK_DIR / f"raw{n:04d}.luau"
        raw.write_text(block.code, encoding="utf-8")
        raw_files[str(raw)] = block

    if not meta:
        return
    proc = subprocess.run(
        [lsp, "analyze", "--flag:LuauSolverV2=true", f"--definitions=@roblox={defs}", "--platform=roblox", *meta.keys()],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    for line in (proc.stdout + proc.stderr).splitlines():
        m = DIAG_RE.match(line.strip())
        if not m:
            continue
        path, lno, msg = m.group(1), int(m.group(2)), m.group(4)
        key = str((ROOT / path).resolve()) if not os.path.isabs(path) else path
        if key not in meta:
            continue
        block, full, shim_line, hot = meta[key]
        if lno == shim_line or any(p in msg for p in IGNORED_PATTERNS):
            continue
        if re.search(r"Unknown type '\w+\.\w+'", msg):
            continue  # type exported by a module whose require can't be resolved outside the project
        if not full and not any(p in msg for p in API_ERROR_PATTERNS):
            continue
        src_lines = Path(key).read_text(encoding="utf-8").splitlines()
        checked = missing_key_is_error(msg, src_lines[lno - 1] if lno <= len(src_lines) else "", classes)
        if checked is None:
            continue
        msg = checked
        orig = lno - shim_line + hot if lno > shim_line else 1
        report.err(block.md, block.start + orig - 1, f"luau: {msg}")

    if stylua:
        for raw, block in raw_files.items():
            proc = subprocess.run(
                [stylua, "--config-path", str(ROOT / "stylua.toml"), "--check", "-"],
                input=block.code,
                capture_output=True,
                text=True,
            )
            if proc.returncode != 0:
                first = next((l for l in proc.stdout.splitlines() if l.startswith(("-", "+")) and not l.startswith(("---", "+++"))), "")
                report.err(block.md, block.start, f"stylua: block is not formatted ({first.strip()[:100]})")
    else:
        report.warnings.append("stylua not found: formatting not checked")


def fix_format(blocks: list[Block]) -> int:
    """Rewrite luau blocks in place using StyLua."""
    stylua = tool("STYLUA", "stylua")
    if not stylua:
        print("stylua not found", file=sys.stderr)
        return 1
    by_file: dict[Path, list[Block]] = {}
    for b in blocks:
        by_file.setdefault(b.md, []).append(b)
    for md, bs in by_file.items():
        lines = md.read_text(encoding="utf-8").splitlines()
        for b in sorted(bs, key=lambda b: b.start, reverse=True):
            proc = subprocess.run(
                [stylua, "--config-path", str(ROOT / "stylua.toml"), "-"], input=b.code, capture_output=True, text=True
            )
            if proc.returncode != 0:
                print(f"{md}:{b.start}: stylua failed: {proc.stderr.strip()}", file=sys.stderr)
                continue
            n = b.code.count("\n")
            lines[b.start - 1 : b.start - 1 + n] = proc.stdout.rstrip("\n").split("\n")
        md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


def check_agents(report: Report) -> None:
    tsv = ROOT / "scripts" / "agents.tsv"
    doc = (ROOT / "docs" / "agents.md").read_text(encoding="utf-8")
    seen: set[str] = set()
    for n, line in enumerate(tsv.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) != 5 or not all(cols):
            report.err(tsv, n, "expected 5 non-empty tab-separated columns")
            continue
        agent, aliases, project, global_dir, _tools = cols
        for name in [agent] + ([] if aliases == "-" else aliases.split(",")):
            if not NAME_RE.match(name) or name in seen:
                report.err(tsv, n, f"agent id or alias {name!r} is invalid or duplicated")
            seen.add(name)
        if project.startswith(("/", "~")) or not re.match(r"^(~|\$CONFIG)/", global_dir):
            report.err(tsv, n, "project dir must be relative; global dir must start with ~/ or $CONFIG/")
        if f"| `{agent}`" not in doc:
            report.err(tsv, n, f"agent {agent!r} is missing from docs/agents.md")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-luau", action="store_true", help="skip luau-lsp / stylua checks")
    ap.add_argument("--fix-format", action="store_true", help="format luau blocks in place with StyLua")
    ap.add_argument("skills", nargs="*", help="only these skill names")
    args = ap.parse_args()

    report = Report()
    blocks: list[Block] = []
    dirs = sorted(d for d in SKILLS.iterdir() if d.is_dir())
    if args.skills:
        dirs = [d for d in dirs if d.name in args.skills]
    for d in dirs:
        blocks += check_skill(d, report)

    if args.fix_format:
        return fix_format(blocks)

    check_agents(report)
    for b in blocks:
        check_deprecated(b, report)
    if not args.no_luau:
        check_luau(blocks, report)

    for w in report.warnings:
        print(f"warning: {w}")
    for e in report.errors:
        print(f"error: {e}")
    print(
        f"\n{len(dirs)} skills, {len(blocks)} luau blocks "
        f"({report.checked_blocks} type-checked, {report.skipped_blocks} nocheck), "
        f"{len(report.errors)} errors, {len(report.warnings)} warnings"
    )
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
