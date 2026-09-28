# Profiling walkthrough

## 1. Classify the problem

| Observation | Look at |
| --- | --- |
| Low FPS for everyone, server fine | Client MicroProfiler (render vs script vs physics). |
| Everyone lags at once, ping spikes | Server: Dev Console → Server Stats heartbeat, server MicroProfiler, Script Profiler (server). |
| Only mobile crashes | Client memory categories, textures, sounds, streaming settings. |
| Degrades over session length | Memory leak: heap snapshots over time, unparented instances. |

## 2. MicroProfiler

1. Ctrl+Alt+F6 (client) or Dev Console → MicroProfiler (server). Pause (Ctrl+P) on a spike frame.
2. Read the frame: `Render` (GPU/CPU render prep), `Physics`/`worldStep`, `Heartbeat`/`RunService`,
   `Replicator`/`ProcessPackets` (network), `WaitingForGPU` (GPU bound).
3. Expand script scopes: your `debug.profilebegin` labels appear under `$Script`/Heartbeat.
4. Dump (Dev Console → MicroProfiler → Dump) to an HTML file for offline analysis. Roblox Assistant's
   `rbx-perf-profiling` skill and the Studio MCP can interpret dumps.

## 3. Script Profiler

Start recording (client or server), reproduce the lag for 10–30 s, stop, sort by total/self time.
Look for functions called far more often than expected (per-frame loops, event storms).

## 4. Memory leaks

1. Dev Console → Memory: which category grows (`LuaHeap`, `Instances`, `Signals`, `PhysicsParts`...)?
2. Luau Heap: take a snapshot, play for a while, take another, compare. Inspect "Unique references" to
   find which table/closure holds objects.
3. Scene Analysis → **Unparented instances**: instances with `Parent = nil` still referenced from Luau
   (classic: cached characters, UI clones, removed parts kept in tables).
4. Typical culprits:
   - `Players.PlayerAdded` handlers creating connections that are never disconnected.
   - Tables keyed by `Player`/`Instance` never cleared on leave/destroy.
   - `character.Humanoid.Died:Connect` inside `CharacterAdded` capturing big upvalues — OK if the character is
     destroyed (connections are cleaned on `Destroy`), a leak if characters are only reparented.
   - Instances removed with `Parent = nil` instead of `:Destroy()`.

```luau
--!strict
-- Pattern: per-player cleanup bag.
local Players = game:GetService("Players")

local bags: { [Player]: { () -> () } } = {}

local function track(player: Player, cleanup: () -> ())
	local bag = bags[player]
	if not bag then
		bag = {}
		bags[player] = bag
	end
	table.insert(bag, cleanup)
end

Players.PlayerRemoving:Connect(function(player)
	for _, cleanup in bags[player] or {} do
		task.spawn(cleanup)
	end
	bags[player] = nil
end)

return track
```

## 5. Verify

Re-measure after each change on the **lowest-end target device** (or the Device Emulator plus a real
phone), in a live server with realistic player counts — Studio's single-player timings hide server load.
