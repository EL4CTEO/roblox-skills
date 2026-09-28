# MemoryStore and MessagingService recipes

## Matchmaking queue (MemoryStoreQueue)

```luau
--!strict
local MemoryStoreService = game:GetService("MemoryStoreService")

local queue = MemoryStoreService:GetQueue("Ranked1v1", 30) -- 30 s invisibility timeout
local EXPIRATION = 300

local function enqueue(player: Player)
	local ok, err = pcall(function()
		queue:AddAsync({ userId = player.UserId, rating = 1000 }, EXPIRATION)
	end)
	if not ok then
		warn("enqueue failed:", err)
	end
end

-- One matchmaker loop (e.g. on every server, or a dedicated lobby server).
local function matchmakeOnce()
	local ok, items, readId = pcall(function()
		return queue:ReadAsync(2, true, 5) -- exactly 2 items or none; wait up to 5 s
	end)
	if not ok or not items or #items < 2 then
		return
	end
	-- Reserve a server and teleport both players (see roblox-teleport-matchmaking) ...
	-- Only after success, remove the items; otherwise they reappear after the invisibility timeout.
	pcall(function()
		queue:RemoveAsync(readId)
	end)
end

return { enqueue = enqueue, matchmakeOnce = matchmakeOnce }
```

For many game modes and skill-based matching, prefer Roblox's built-in **matchmaking** (configurable
scoring for which server a player joins) where it fits, and see `roblox-teleport-matchmaking`.

## Live leaderboard / server list (MemoryStoreSortedMap)

```luau
--!strict
local MemoryStoreService = game:GetService("MemoryStoreService")

local servers = MemoryStoreService:GetSortedMap("ActiveServers")

local function heartbeat(playerCount: number)
	pcall(function()
		-- value, expiration (s), sort key: sorts by player count
		servers:SetAsync(game.JobId, { players = playerCount, placeId = game.PlaceId }, 60, playerCount)
	end)
end

local function topServers(): { any }
	local ok, entries = pcall(function()
		return servers:GetRangeAsync(Enum.SortDirection.Descending, 20)
	end)
	return if ok then entries else {}
end

return { heartbeat = heartbeat, topServers = topServers }
```

Entries are `{ key, value, sortKey }`. Refresh with a TTL shorter than the heartbeat interval × 2 so
dead servers disappear on their own.

## Atomic counters (MemoryStoreHashMap)

```luau
--!strict
local MemoryStoreService = game:GetService("MemoryStoreService")

local counters = MemoryStoreService:GetHashMap("EventCounters")

local function increment(name: string, by: number): number?
	local ok, result = pcall(function()
		return counters:UpdateAsync(name, function(old: number?)
			return (old or 0) + by
		end, 86400)
	end)
	return if ok then result else nil
end

return increment
```

## Cross-server announcements (MessagingService)

```luau
--!strict
local MessagingService = game:GetService("MessagingService")
local Players = game:GetService("Players")

local TOPIC = "Announcements"

local function publish(text: string)
	local ok, err = pcall(function()
		MessagingService:PublishAsync(TOPIC, { text = text, from = game.JobId }) -- ≤ 1 kB
	end)
	if not ok then
		warn("publish failed:", err)
	end
end

task.spawn(function()
	local ok, err = pcall(function()
		MessagingService:SubscribeAsync(TOPIC, function(message)
			local payload = message.Data -- message.Sent is the publish timestamp
			if typeof(payload) == "table" and typeof(payload.text) == "string" then
				for _, player in Players:GetPlayers() do
					print(`announce to {player.Name}: {payload.text}`)
				end
			end
		end)
	end)
	if not ok then
		warn("subscribe failed:", err)
	end
end)

return publish
```

- Any text shown to players that originated from a player must be filtered (`roblox-text-chat`).
- Messages can be missed (server starting, throttling). For state that must converge, store it in a
  DataStore/MemoryStore and use messages only as a "go re-read" hint.

## Data store vs memory store

| | DataStore | MemoryStore |
| --- | --- | --- |
| Durability | Persistent, versioned | Expires (≤ 45 days); evicted at quota |
| Latency | Higher | Low |
| Use | Player progress, purchases, anything valuable | Queues, live rankings, sessions, locks, caches |
