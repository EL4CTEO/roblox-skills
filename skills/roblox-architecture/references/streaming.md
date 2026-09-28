# Instance streaming — settings and client patterns

Source: Roblox "Instance streaming" and "Techniques and conversion" docs (2026).

## Recommended Workspace settings

| Property | Value |
| --- | --- |
| `StreamingEnabled` | `true` (default for new places; required by server authority) |
| `ModelStreamingBehavior` | `Improved` |
| `StreamingIntegrityMode` | `PauseOutsideLoadedArea` |
| `StreamingMinRadius` | `64` (default) |
| `StreamingTargetRadius` | `1024` (default) |
| `StreamOutBehavior` | `Opportunistic` (lowers client memory, prevents OOM crashes) |
| `EnableSLIMAvatars` | `Enabled` (lightweight stand-ins for distant R15 avatars) |

## Model settings

- `Model.ModelStreamingMode`:
  - `Default`/`Nonatomic` — parts stream individually.
  - `Atomic` — all **initial** descendants arrive together; scripts can index children directly once the
    model exists. Instances added later are not atomic.
  - `Persistent` — always present on every client, never streams out. Use sparingly (memory).
  - `PersistentPerPlayer` — persistent only for players added via `Model:AddPersistentPlayer(player)`.
- `Model.LevelOfDetail = SLIM` for static models: distant models render as optimized composite meshes.
  Not for animated or runtime-modified models.
- Keep models spatially compact (≈64 studs extents); split huge "container" models; flatten nesting
  (a persistent model inside an atomic one forces the parent persistent).

## Client script patterns

| Pattern | Problem under streaming | Fix |
| --- | --- | --- |
| `workspace.House1.Door` | Errors if not streamed in. | `WaitForChild` (with timeout if optional), nil-check, or make `House1` Atomic. |
| `character.Humanoid` in `CharacterAdded` | Character is parented before descendants replicate. | `character:WaitForChild("Humanoid")`. |
| Remote carries an `Instance` | Signal can arrive before (or without) the instance. | `WaitForChild` with timeout, pre-stream with `RequestStreamAroundAsync`, or tolerate `nil`. |
| Reading `part.Position` of a far part | Returns the last replicated (stale) value. | Do distance logic on the server, or check `part:IsDescendantOf(workspace)`. |
| `folder:GetChildren()` / `GetDescendants()` | Only streamed-in subset. | Enumerate on the server, or `PersistentPerPlayer`, or document that partial is fine. |
| Client raycasts / `GetPartBoundsInBox` | Only streamed-in geometry. | Full-world queries on the server; local-radius queries are fine. |
| `ChildAdded` / tag added signals | Fire again on every stream-in. | Mark first-time effects with an attribute; treat add/remove as stream in/out. |
| Cloning map from ReplicatedStorage on client | Client copy never receives server updates; can stream out. | Build the world on the server. |
| Loading screen waits for a map part | Hangs: no replication focus before spawn. | Wait for character + surroundings, or `player:AddReplicationFocus(part)` before spawn. |
| `Sound`/`AudioPlayer` in a far part | Stops when the part streams out. | Parent ambient audio to a persistent model or `SoundService`. |
| `Touched`, `ProximityPrompt`, `ClickDetector` | Don't work for clients without the part. | Expected; keep interactions local to the player. |
| Client pathfinding | Sees only streamed geometry. | Compute paths on the server. |

```luau
--!strict
local Players = game:GetService("Players")

local player = Players.LocalPlayer

local function onCharacterAdded(character: Model)
	local humanoid = character:WaitForChild("Humanoid", 10) :: Humanoid?
	if not humanoid then
		warn("Humanoid did not replicate in time")
		return
	end
	print("walk speed", humanoid.WalkSpeed)
end

if player.Character then
	task.spawn(onCharacterAdded, player.Character)
end
player.CharacterAdded:Connect(onCharacterAdded)
```

## Proactive streaming (server)

```luau
--!strict
local function teleportCharacter(player: Player, target: CFrame)
	local ok, err = pcall(function()
		player:RequestStreamAroundAsync(target.Position, 5) -- optional timeout in seconds
	end)
	if not ok then
		warn(err)
	end
	local character = player.Character
	if character and character.Parent then
		character:PivotTo(target)
	end
end

return teleportCharacter
```

`Player:AddReplicationFocus(part)` / `RemoveReplicationFocus(part)` keep an extra area loaded for a player
(e.g. a camera cutscene location). Keep the number of extra foci small.

## Testing

- Test with `StreamingTargetRadius = 64` to surface bugs.
- Traverse the whole map, teleport between distant areas, revisit areas.
- Watch Output/Developer Console for `attempt to index nil with ...`.
- Roblox publishes an official AI **streaming conversion skill** (`/rbx-convert-to-streaming`) that runs
  through the Studio MCP server; see the `roblox-studio-mcp` skill.
