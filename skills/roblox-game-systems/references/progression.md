# Progression recipes

## leaderstats (player list display)

```luau
--!strict
local Players = game:GetService("Players")

local function setupLeaderstats(player: Player)
	local leaderstats = Instance.new("Folder")
	leaderstats.Name = "leaderstats" -- exact lowercase name is required

	local coins = Instance.new("IntValue")
	coins.Name = "Coins"
	local function sync()
		local value = player:GetAttribute("Coins")
		coins.Value = if typeof(value) == "number" then value else 0
	end
	sync()
	coins.Parent = leaderstats
	player:GetAttributeChangedSignal("Coins"):Connect(sync)

	leaderstats.Parent = player
end

Players.PlayerAdded:Connect(setupLeaderstats)
for _, player in Players:GetPlayers() do
	task.spawn(setupLeaderstats, player)
end
```

`leaderstats` values are display only — the source of truth stays in the service/data layer.

## XP and levels

```luau
--!strict
local Levels = {}

-- XP needed to go from `level` to `level + 1`: gentle exponential curve.
function Levels.xpForLevel(level: number): number
	return math.floor(100 * level ^ 1.5)
end

-- Adds XP and returns the new (level, xp, levelsGained). Pure: easy to unit test.
function Levels.addXp(level: number, xp: number, amount: number, maxLevel: number): (number, number, number)
	local gained = 0
	xp += amount
	while level < maxLevel and xp >= Levels.xpForLevel(level) do
		xp -= Levels.xpForLevel(level)
		level += 1
		gained += 1
	end
	if level >= maxLevel then
		xp = 0
	end
	return level, xp, gained
end

print(Levels.addXp(1, 0, 450, 100))
return Levels
```

## Daily rewards with streaks (server)

```luau
--!strict
type RewardState = { lastClaimDay: number?, streak: number }

local REWARDS = { 50, 75, 100, 150, 200, 300, 500 } -- day 1..7, then repeat day 7

local function utcDay(): number
	return os.time() // 86400
end

-- Returns (granted amount or nil, reason). Mutates `state`.
local function claimDaily(state: RewardState): (number?, string)
	local today = utcDay()
	if state.lastClaimDay == today then
		return nil, "already claimed"
	end
	if state.lastClaimDay == today - 1 then
		state.streak += 1
	else
		state.streak = 1 -- missed a day (or first claim)
	end
	state.lastClaimDay = today
	return REWARDS[math.min(state.streak, #REWARDS)], "ok"
end

local state: RewardState = { streak = 0 }
print(claimDaily(state))
return claimDaily
```

Store `RewardState` in the player's profile; call from a rate-limited remote; save immediately after.
Show the next claim time using `(utcDay() + 1) * 86400` and `workspace:GetServerTimeNow()` on the client.

## Obby checkpoints (server-validated)

```luau
--!strict
local CollectionService = game:GetService("CollectionService")
local Players = game:GetService("Players")

local stageOf: { [Player]: number } = {}

local function onCheckpoint(checkpoint: BasePart)
	local stage = checkpoint:GetAttribute("Stage")
	if typeof(stage) ~= "number" then
		return
	end
	checkpoint.Touched:Connect(function(hit)
		local character = hit:FindFirstAncestorOfClass("Model")
		local player = character and Players:GetPlayerFromCharacter(character)
		if not player then
			return
		end
		local current = stageOf[player] or 0
		if stage == current + 1 then -- only the next stage counts (no skipping ahead)
			stageOf[player] = stage
			player:SetAttribute("Stage", stage)
		end
	end)
end

for _, checkpoint in CollectionService:GetTagged("Checkpoint") do
	if checkpoint:IsA("BasePart") then
		onCheckpoint(checkpoint)
	end
end

Players.PlayerAdded:Connect(function(player)
	player.CharacterAdded:Connect(function(character)
		local stage = stageOf[player] or 0
		for _, checkpoint in CollectionService:GetTagged("Checkpoint") do
			if checkpoint:IsA("BasePart") and checkpoint:GetAttribute("Stage") == stage then
				task.defer(function()
					character:PivotTo(checkpoint.CFrame + Vector3.new(0, 4, 0))
				end)
			end
		end
	end)
end)

Players.PlayerRemoving:Connect(function(player)
	stageOf[player] = nil
end)
```

Add timing heuristics (minimum plausible time per stage) to flag teleport exploits (`roblox-security`).
