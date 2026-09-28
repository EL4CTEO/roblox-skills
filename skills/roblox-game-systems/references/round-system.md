# Round-based game loop

State machine on the server; clients render from replicated attributes on a shared instance.
Timers use absolute end times so clients count down locally without per-second remotes.

```luau
--!strict
-- ServerScriptService/Server/Services/RoundService.luau
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")
local Teams = game:GetService("Teams")

type Phase = "Waiting" | "Intermission" | "Playing" | "Results"

local MIN_PLAYERS = 2
local INTERMISSION = 15
local ROUND_LENGTH = 180
local RESULTS = 8

-- Shared state instance: clients read attributes (Phase, PhaseEndsAt, Map, Winner).
local state = Instance.new("Folder")
state.Name = "RoundState"
state.Parent = ReplicatedStorage

local maps = ServerStorage:WaitForChild("Maps")
local lobbySpawn = workspace:WaitForChild("LobbySpawn") :: BasePart

local participants: { [Player]: boolean } = {}
local currentMap: Model? = nil

local function setPhase(phase: Phase, duration: number?)
	state:SetAttribute("Phase", phase)
	state:SetAttribute("PhaseEndsAt", if duration then workspace:GetServerTimeNow() + duration else nil)
end

local function aliveParticipants(): { Player }
	local alive = {}
	for player in participants do
		local character = player.Character
		local humanoid = character and character:FindFirstChildOfClass("Humanoid")
		if player.Parent == Players and humanoid and humanoid.Health > 0 then
			table.insert(alive, player)
		end
	end
	return alive
end

local function loadMap(): Model
	local choices = maps:GetChildren()
	local template = choices[math.random(1, #choices)] :: Model
	local map = template:Clone()
	map.Parent = workspace
	state:SetAttribute("Map", template.Name)
	return map
end

local function teleportTo(player: Player, target: CFrame)
	local character = player.Character
	if character then
		character:PivotTo(target + Vector3.new(0, 4, 0))
	end
end

local function startRound()
	currentMap = loadMap()
	local spawns = (currentMap :: Model):WaitForChild("Spawns"):GetChildren()
	local red, blue = Teams:FindFirstChild("Red") :: Team?, Teams:FindFirstChild("Blue") :: Team?
	for index, player in Players:GetPlayers() do
		participants[player] = true
		if red and blue then
			player.Team = if index % 2 == 0 then red else blue
		end
		local spawnPart = spawns[(index - 1) % #spawns + 1] :: BasePart
		teleportTo(player, spawnPart.CFrame)
	end
end

local function endRound(winner: string)
	state:SetAttribute("Winner", winner)
	for player in participants do
		teleportTo(player, lobbySpawn.CFrame)
		player.Neutral = true
	end
	table.clear(participants)
	if currentMap then
		currentMap:Destroy()
		currentMap = nil
	end
end

Players.PlayerRemoving:Connect(function(player)
	participants[player] = nil -- leaving mid-round must not break win checks
end)

local function run()
	while true do
		if #Players:GetPlayers() < MIN_PLAYERS then
			setPhase("Waiting")
			repeat
				task.wait(1)
			until #Players:GetPlayers() >= MIN_PLAYERS
		end

		setPhase("Intermission", INTERMISSION)
		task.wait(INTERMISSION)
		if #Players:GetPlayers() < MIN_PLAYERS then
			continue
		end

		startRound()
		setPhase("Playing", ROUND_LENGTH)
		local deadline = os.clock() + ROUND_LENGTH
		local winner = "Nobody"
		while os.clock() < deadline do
			local alive = aliveParticipants()
			if #alive <= 1 then
				winner = if alive[1] then alive[1].Name else "Nobody"
				break
			end
			task.wait(0.5)
		end

		setPhase("Results", RESULTS)
		endRound(winner)
		task.wait(RESULTS)
	end
end

task.spawn(run)
return {}
```

## Client countdown

```luau
--!strict
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local state = ReplicatedStorage:WaitForChild("RoundState")

RunService.Heartbeat:Connect(function()
	local endsAt = state:GetAttribute("PhaseEndsAt")
	local phase = state:GetAttribute("Phase")
	if typeof(endsAt) == "number" then
		local remaining = math.max(0, math.ceil(endsAt - workspace:GetServerTimeNow()))
		-- update a TextLabel only when `remaining` changes
		local _text = `{phase}: {remaining}s`
	end
end)
```

## Variations

- **Teams**: create `Team` objects in `Teams` (`AutoAssignable = false` when you assign manually); set
  `player.Team`; team spawns via `SpawnLocation.TeamColor`.
- **Late joiners** during `Playing`: spectate (camera on a random alive player) until next round.
- **Rewards**: grant through the currency service at `Results` for participants still in the server.
- **Round per reserved server** (competitive): the lobby teleports a full match to a reserved server
  that runs exactly one round, then teleports everyone back (`roblox-teleport-matchmaking`).
