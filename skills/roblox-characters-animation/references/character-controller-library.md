# Character Controller Library (CCL) — beta

Source: Roblox "Character Controller Library" and "Custom abilities" docs (2026). Beta: enable
**File → Beta Features → AvatarAbilities Character Controller Library**, then **Avatar Settings →
Movement → Abilities → Character Controller Library**. APIs may change; re-check the docs.

## Concepts

- **Ability**: a table (`AvatarAbilities.AbilityDefinition`) in a ModuleScript shared by server and client.
- **Labels**: named bits in a 64-bit world mask. Active abilities broadcast `Labels`; `TimedLabels`
  (`OnStart`, `OnStop` with durations in seconds, `Consumes` list) broadcast or remove labels temporarily.
- **Sensors**: engine facts such as `Identifiers.Sensor.Ground`.
- **Conditions**: `StartsWhen` / `RunsWhile` built from labels, sensors, and `Rule.All`, `Rule.Any`, `Rule.Not`
  (`Not` takes a single label). They compile to bitmask math.
- **Conflicts**: `Blocks`, `Stops`, `Suspends`, `ExclusiveGroup`.
- **Input**: `{ InputName = "Dash", Mode = "Press", ActionSlot = 5 }` — injected into `StartsWhen`.
- **Callbacks**: `OnSetup`, `OnStart`, `OnUpdate`, `OnStop`, `OnTeardown` with
  `(managerCtx: AvatarAbilities.ManagerContext, abilityCtx: AvatarAbilities.AbilityContext)`.
  `managerCtx.AbilityOwner` is the character; `abilityCtx.Config` / `abilityCtx.State` hold per-ability config and replicated state.

## Custom dash ability

```luau
-- ReplicatedStorage/CustomAbilities/Dash (ModuleScript)
local AvatarAbilities = require("@rbx/AvatarAbilities")
local Identifiers = AvatarAbilities.Identifiers
local Rule = AvatarAbilities.Rule
local Sensor = Identifiers.Sensor
local All, Not = Rule.All, Rule.Not

local Dash: AvatarAbilities.AbilityDefinition = {
	Name = "Dash",
	Labels = { "Dashing" },
	StartsWhen = All(Sensor.Ground, Not("DashCooldown")),
	RunsWhile = "DashWindow",
	Input = { InputName = "Dash", Mode = "Press", ActionSlot = 5 },
	TimedLabels = {
		OnStart = { DashWindow = 0.2 }, -- active for 0.2 s
		OnStop = { DashCooldown = 1.0 }, -- then 1 s cooldown
	},
}

function Dash.OnStart(managerCtx: AvatarAbilities.ManagerContext, _abilityCtx: AvatarAbilities.AbilityContext)
	local rootPart = managerCtx.AbilityOwner.PrimaryPart
	if rootPart then
		rootPart:ApplyImpulse(managerCtx.RootLookVector * 80 * rootPart.AssemblyMass)
	end
end

return Dash
```

## Registering abilities (server)

```luau
--!strict
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local AvatarAbilities = require("@rbx/AvatarAbilities")

local CUSTOM_ABILITIES = {
	ReplicatedStorage.CustomAbilities.Dash,
}

local function onCharacterAdded(character: Model)
	local actor = character:WaitForChild("AbilityManagerActor", 10)
	if not actor then
		return
	end
	while not actor:IsDescendantOf(game) do
		actor.AncestryChanged:Wait()
	end
	for _, abilityModule in CUSTOM_ABILITIES do
		AvatarAbilities.addAbilityForCharacter(character, abilityModule) -- pass the module, don't require it
	end
end

local function onPlayerAdded(player: Player)
	player.CharacterAdded:Connect(onCharacterAdded)
	if player.Character then
		task.spawn(onCharacterAdded, player.Character)
	end
end

Players.PlayerAdded:Connect(onPlayerAdded)
for _, player in Players:GetPlayers() do
	onPlayerAdded(player)
end
```

Callbacks run in both the predicted client simulation and the authoritative server simulation: keep
them deterministic (no `math.random` without shared seeds, no client-only state).
