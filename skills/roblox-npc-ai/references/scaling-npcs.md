# Scaling NPCs

## Spawning and pooling

```luau
--!strict
local CollectionService = game:GetService("CollectionService")
local ServerStorage = game:GetService("ServerStorage")

local template = ServerStorage:WaitForChild("Enemies"):WaitForChild("Zombie") :: Model
local pool: { Model } = {}
local POOL_PARENT = ServerStorage

local function spawnEnemy(at: CFrame): Model
	local npc = table.remove(pool) or template:Clone()
	local humanoid = npc:FindFirstChildOfClass("Humanoid")
	if humanoid then
		humanoid.Health = humanoid.MaxHealth
	end
	npc:PivotTo(at)
	npc.Parent = workspace
	if npc.PrimaryPart then
		npc.PrimaryPart:SetNetworkOwner(nil) -- must be in Workspace first
	end
	CollectionService:AddTag(npc, "Enemy")
	return npc
end

local function despawnEnemy(npc: Model)
	CollectionService:RemoveTag(npc, "Enemy")
	npc.Parent = POOL_PARENT
	table.insert(pool, npc)
end

return { spawn = spawnEnemy, despawn = despawnEnemy }
```

- Pooling avoids replication cost of creating/destroying complex models repeatedly. Reset every piece of
  state (health, attributes, velocity, animations) when reusing.
- Humanoids with `BreakJointsOnDeath = true` can't be reused after death — set it `false` for pooled NPCs.
- Set `Humanoid.RequiresNeck = false` only if your NPC rig has no neck joint.

## Performance levers (measure with the MicroProfiler first)

| Cost | Lever |
| --- | --- |
| Humanoid physics/state machine | Fewer Humanoids: `AnimationController` + anchored/CFrame movement for simple mobs; disable unused states (`SetStateEnabled(Enum.HumanoidStateType.Climbing, false)`, `Swimming`, `Ragdoll`, `FallingDown`). |
| Pathfinding | Share paths between NPCs heading to the same goal; flow fields/grids for hordes; lower recompute rate. |
| AI thinking | Fixed think rate (5–10 Hz), staggered; skip NPCs far from all players. |
| Replication | Fewer parts per NPC (MeshParts), no unnecessary descendants, avoid per-frame property changes on the server. |
| Animation | Let clients animate NPCs (server sets an attribute like `State = "Run"`, clients play tracks). |
| Heavy math (steering, flocking) | `--!native` module; Parallel Luau `Actor`s with `task.desynchronize()` for read-only computation, then `task.synchronize()` to write. |
| Rendering far NPCs | Streaming + `Model.LevelOfDetail`; hide/disable NPCs outside interest range. |

## Client-simulated crowds

For hundreds of purely cosmetic NPCs (city crowds, ambient animals), simulate on clients only:
the server sends a seed + spawn areas, each client spawns and animates locally. Nothing gameplay-
relevant can depend on these NPCs, because every client sees slightly different positions.
