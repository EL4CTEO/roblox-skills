# Player data with raw DataStoreService (session-locked)

Use this when a project can't use ProfileStore. It shows every moving part: session lock, retries,
autosave with jitter, and shutdown flushing. Keep it in `ServerScriptService`.

```luau
--!strict
local DataStoreService = game:GetService("DataStoreService")
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local STORE = DataStoreService:GetDataStore("PlayerData")
local AUTOSAVE_INTERVAL = 180
local LOCK_EXPIRY = 600 -- a lock older than this is considered abandoned (crashed server)
local SERVER_ID = if RunService:IsStudio() then "studio-" .. HttpService:GenerateGUID(false) else game.JobId

type PlayerData = { version: number, coins: number, inventory: { [string]: number } }
type Record = { data: PlayerData, lock: { server: string, time: number }? }

local function defaultData(): PlayerData
	return { version = 1, coins = 0, inventory = {} }
end

local sessions: { [Player]: PlayerData } = {}

local function withRetries<T>(label: string, fn: () -> T): (boolean, T?)
	local waitTime = 1
	for attempt = 1, 5 do
		local ok, result = pcall(fn)
		if ok then
			return true, result
		end
		warn(`{label} failed (attempt {attempt}): {result}`)
		task.wait(waitTime + math.random())
		waitTime = math.min(waitTime * 2, 16)
	end
	return false, nil
end

local function keyFor(player: Player): string
	return `User_{player.UserId}`
end

-- Acquire the session lock and return the data, or nil if another live server holds it.
local function load(player: Player): PlayerData?
	local loaded: PlayerData? = nil
	local ok = withRetries("load", function()
		STORE:UpdateAsync(keyFor(player), function(record: Record?): Record?
			local now = os.time()
			local current: Record = record or { data = defaultData(), lock = nil }
			local lock = current.lock
			if lock and lock.server ~= SERVER_ID and now - lock.time < LOCK_EXPIRY then
				loaded = nil
				return nil -- cancel the write: someone else owns this session
			end
			current.lock = { server = SERVER_ID, time = now }
			loaded = current.data
			return current
		end)
		return true
	end)
	return if ok then loaded else nil
end

local function save(player: Player, release: boolean)
	local data = sessions[player]
	if not data then
		return
	end
	withRetries("save", function()
		STORE:UpdateAsync(keyFor(player), function(record: Record?): (Record?, { number }?)
			if record and record.lock and record.lock.server ~= SERVER_ID then
				return nil, nil -- we lost the lock; never overwrite another server's session
			end
			local newRecord: Record = {
				data = data,
				lock = if release then nil else { server = SERVER_ID, time = os.time() },
			}
			return newRecord, { player.UserId } -- user IDs link the key for right-to-be-forgotten
		end)
		return true
	end)
end

local function onPlayerAdded(player: Player)
	local data = nil
	for _ = 1, 3 do -- the previous server may still be releasing the lock after a teleport
		data = load(player)
		if data or player.Parent ~= Players then
			break
		end
		task.wait(5)
	end
	if player.Parent ~= Players then
		return
	end
	if not data then
		player:Kick("Your data is still in use on another server. Please rejoin shortly.")
		return
	end
	sessions[player] = data
end

Players.PlayerAdded:Connect(onPlayerAdded)
for _, player in Players:GetPlayers() do
	task.spawn(onPlayerAdded, player)
end

Players.PlayerRemoving:Connect(function(player)
	save(player, true)
	sessions[player] = nil
end)

task.spawn(function()
	task.wait(math.random() * AUTOSAVE_INTERVAL) -- stagger servers
	while true do
		for player in sessions do
			task.spawn(save, player, false)
		end
		task.wait(AUTOSAVE_INTERVAL)
	end
end)

game:BindToClose(function()
	if RunService:IsStudio() then
		task.wait(1) -- let PlayerRemoving saves start in Studio
	end
	local pending = 0
	for player in sessions do
		pending += 1
		task.spawn(function()
			save(player, true)
			pending -= 1
		end)
	end
	while pending > 0 do
		task.wait()
	end
end)
```

## Notes

- `UpdateAsync`'s transform can run more than once (on conflicts); keep it side-effect free apart from
  capturing the result as above.
- `BindToClose` has about 30 seconds in total. Save all players in parallel, not sequentially.
- A kicked or crashed server leaves a stale lock; `LOCK_EXPIRY` recovers after 10 minutes. ProfileStore
  resolves conflicts faster by messaging the lock holder.
- In Studio, use a separate data store name (e.g. `PlayerData_Studio`) or a separate test universe.
- Log failures to analytics; if a save ultimately fails on leave, the next server loads the last
  good version — never write partial or default data over a failed load.
