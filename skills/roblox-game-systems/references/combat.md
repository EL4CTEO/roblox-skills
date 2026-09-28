# Server-validated combat

Clients predict (play the swing/shot instantly) and send **intent**; the server owns cooldowns, hit
detection or hit validation, and damage.

## Weapon config (shared)

```luau
--!strict
-- ReplicatedStorage/Shared/WeaponConfig.luau
export type Weapon = {
	kind: "Melee" | "Ranged",
	damage: number,
	cooldown: number,
	range: number,
	hitboxSize: Vector3?, -- melee
}

return table.freeze({
	Sword = { kind = "Melee", damage = 25, cooldown = 0.6, range = 7, hitboxSize = Vector3.new(6, 5, 7) },
	Blaster = { kind = "Ranged", damage = 18, cooldown = 0.25, range = 300 },
} :: { [string]: Weapon })
```

## Server combat service

```luau
--!strict
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local WeaponConfig = require(ReplicatedStorage.Shared.WeaponConfig)

local attackRemote = Instance.new("RemoteEvent")
attackRemote.Name = "Attack"
attackRemote.Parent = ReplicatedStorage

local lastAttack: { [Player]: number } = {}
local equipped: { [Player]: string } = {} -- set by the inventory/tool system, never by the client

local overlap = OverlapParams.new()
overlap.FilterType = Enum.RaycastFilterType.Exclude
local rayParams = RaycastParams.new()
rayParams.FilterType = Enum.RaycastFilterType.Exclude

local function rootOf(player: Player): BasePart?
	local character = player.Character
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	if not humanoid or humanoid.Health <= 0 then
		return nil
	end
	return humanoid.RootPart
end

local function damageModel(model: Model, attacker: Player, amount: number)
	local humanoid = model:FindFirstChildOfClass("Humanoid")
	local victim = Players:GetPlayerFromCharacter(model)
	if not humanoid or humanoid.Health <= 0 or victim == attacker then
		return
	end
	if victim and victim.Team and victim.Team == attacker.Team and not victim.Neutral then
		return -- no friendly fire
	end
	humanoid:SetAttribute("LastAttacker", attacker.UserId)
	humanoid:TakeDamage(amount)
end

local function meleeAttack(player: Player, root: BasePart, damage: number, range: number, hitboxSize: Vector3)
	-- Server-side hitbox in front of the attacker (uses server positions: no client-reported targets).
	local boxCFrame = root.CFrame * CFrame.new(0, 0, -range / 2)
	overlap.FilterDescendantsInstances = { player.Character :: Model }
	local hitModels: { [Model]: boolean } = {}
	for _, part in workspace:GetPartBoundsInBox(boxCFrame, hitboxSize, overlap) do
		local model = part:FindFirstAncestorOfClass("Model")
		if model and not hitModels[model] then
			hitModels[model] = true
			damageModel(model, player, damage)
		end
	end
end

local function rangedAttack(player: Player, root: BasePart, damage: number, range: number, direction: Vector3)
	-- Client sends only an aim direction; the server casts from its own muzzle position.
	local origin = root.Position + Vector3.new(0, 1.5, 0)
	local offset = direction.Unit * range
	rayParams.FilterDescendantsInstances = { player.Character :: Model }
	local result = workspace:Raycast(origin, offset, rayParams)
	if result then
		local model = result.Instance:FindFirstAncestorOfClass("Model")
		if model then
			damageModel(model, player, damage)
		end
	end
	attackRemote:FireAllClients(player, origin, if result then result.Position else origin + offset)
end

attackRemote.OnServerEvent:Connect(function(player: Player, direction: unknown)
	local weaponName = equipped[player]
	local weapon = weaponName and WeaponConfig[weaponName]
	local root = rootOf(player)
	if not weapon or not root then
		return
	end
	local now = os.clock()
	if now - (lastAttack[player] or 0) < weapon.cooldown * 0.9 then -- small tolerance for jitter
		return
	end
	lastAttack[player] = now

	if weapon.kind == "Melee" then
		meleeAttack(player, root, weapon.damage, weapon.range, weapon.hitboxSize or Vector3.one * 5)
	elseif
		typeof(direction) == "Vector3"
		and direction.Magnitude > 0.01
		and direction.Magnitude == direction.Magnitude
	then
		rangedAttack(player, root, weapon.damage, weapon.range, direction) -- Magnitude == Magnitude rejects NaN
	end
end)

Players.PlayerRemoving:Connect(function(player)
	lastAttack[player] = nil
	equipped[player] = nil
end)

return { equipped = equipped }
```

## Lag compensation (fast shooters)

Server-side raycasts against **current** server positions miss targets the shooter saw earlier.
Options:
- **Hit claims + validation**: client reports `(targetCharacter, hitPosition, clientTime)`; server checks
  the target was within tolerance of that position recently (keep a short position history per
  character, ~1 s, sampled on Heartbeat, rewound by `player:GetNetworkPing()`), line of sight against
  static geometry, range, and fire rate.
- **Server authority** mode handles prediction/rollback for you (`roblox-physics`).

## Client side

- On input: play the animation/sound/muzzle flash immediately, then `Attack:FireServer(aimDirection)`.
- On `Attack.OnClientEvent(shooter, from, to)`: draw tracers for other players' shots (skip your own if
  already predicted).
- Health bars read `Humanoid.Health`; damage numbers from a server event carrying `(target, amount)`.
- Use `GetMarkerReachedSignal` on swing animations to time client VFX; the server uses its own timing.
