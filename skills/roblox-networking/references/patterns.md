# Networking patterns

## Request/response without RemoteFunction hangs

`InvokeServer` is fine (the server always answers), but the server handler must never yield forever
and must return quickly. Wrap slow work (DataStore) and always return a result table.

```luau
--!strict
-- Server
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Net = require(ReplicatedStorage.Shared.Net)

type StockResult = { ok: true, stock: { [string]: number } } | { ok: false, reason: string }

local stock: { [string]: number } = { Sword = 5 }

Net.GetShopStock.OnServerInvoke = function(_player: Player): StockResult
	-- Never yield indefinitely here: the client is blocked until you return.
	return { ok = true, stock = table.clone(stock) }
end
```

Client side, add a timeout so UI never freezes if the server is slow:

```luau
--!strict
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Net = require(ReplicatedStorage.Shared.Net)

local function invokeWithTimeout(remote: RemoteFunction, timeout: number, ...: any): (boolean, any)
	local thread = coroutine.running()
	local done = false
	local args = table.pack(...)
	task.spawn(function()
		local result = table.pack(pcall(remote.InvokeServer, remote, table.unpack(args, 1, args.n)))
		if not done then
			done = true
			task.spawn(thread, table.unpack(result, 1, result.n))
		end
	end)
	task.delay(timeout, function()
		if not done then
			done = true
			task.spawn(thread, false, "timeout")
		end
	end)
	return coroutine.yield()
end

local ok, result = invokeWithTimeout(Net.GetShopStock, 5)
print(ok, result)
```

## State replication: snapshot + deltas

For per-player private state (inventory, quests) keep the truth on the server and send one snapshot
on join, then small deltas. Clients apply deltas to their copy and fire local signals for UI.

```luau
--!strict
-- Server: InventoryService (excerpt)
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Net = require(ReplicatedStorage.Shared.Net)

type Inventory = { [string]: number }
local inventories: { [Player]: Inventory } = {}

local function sendSnapshot(player: Player)
	Net.InventoryChanged:FireClient(player, "snapshot", inventories[player])
end

local function addItem(player: Player, itemId: string, amount: number)
	local inventory = inventories[player]
	if not inventory then
		return
	end
	local newCount = (inventory[itemId] or 0) + amount
	inventory[itemId] = if newCount > 0 then newCount else nil
	Net.InventoryChanged:FireClient(player, "delta", itemId, inventory[itemId] or 0)
end

return { sendSnapshot = sendSnapshot, addItem = addItem, inventories = inventories }
```

Shared, public state (round phase, scores) is simpler as attributes on a replicated instance (for
example `ReplicatedStorage.GameState:SetAttribute("Phase", "Intermission")`) — clients listen with
`GetAttributeChangedSignal`.

## Per-frame batching

```luau
--!strict
local RunService = game:GetService("RunService")

local remote = Instance.new("RemoteEvent")
local queue: { { any } } = {}

local function send(...: any)
	table.insert(queue, table.pack(...))
end

RunService.Heartbeat:Connect(function()
	if #queue == 0 then
		return
	end
	local batch = queue
	queue = {}
	remote:FireAllClients(batch) -- one packet instead of many
end)

send("hit", 1, 25)
```

## Client prediction for responsiveness

1. Client plays the action immediately (animation, sound, local VFX, UI change).
2. Client fires the request with the minimum data (e.g. aim direction, target id, client timestamp).
3. Server validates against **its** state (cooldowns, range, ammo, line of sight with ping allowance)
   and applies the authoritative result.
4. Server broadcasts the result; the originating client reconciles (e.g. rolls back ammo if rejected).

For competitive games, Roblox's built-in **server authority** model (client prediction + rollback,
`RunService:BindToSimulation`) handles movement/physics prediction for you — see `roblox-security`
and `roblox-physics`.

## Unreliable events done right

```luau
--!strict
-- Client: stream aim direction at most 20 times per second.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Net = require(ReplicatedStorage.Shared.Net)

local SEND_INTERVAL = 1 / 20
local accumulator = 0
local lastSent = Vector3.zero

RunService.Heartbeat:Connect(function(deltaTime)
	accumulator += deltaTime
	if accumulator < SEND_INTERVAL then
		return
	end
	accumulator = 0
	local camera = workspace.CurrentCamera
	if not camera then
		return
	end
	local direction = camera.CFrame.LookVector
	if direction:FuzzyEq(lastSent, 1e-3) then
		return -- unchanged: send nothing
	end
	lastSent = direction
	Net.AimDirection:FireServer(direction)
end)
```

- Each message must make sense on its own (full value, not a delta), since earlier ones may be lost.
- Keep payloads far below 1000 bytes.

## Schema-driven networking (Zap / Blink style)

Define events once in a schema file; the generator emits `client.luau` and `server.luau` modules with
typed `Fire`/`On` functions, validation, and buffer packing. Typical schema shape:

```text
event DamageDealt = {
    from: Server,
    type: Reliable,
    call: SingleSync,
    data: struct { target: u32, amount: u16, critical: boolean },
}
```

Check the generator's docs for exact syntax — it differs between tools and versions.
