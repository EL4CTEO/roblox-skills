# Server authority model

Source: Roblox "Server authority model" and "Server authority techniques" docs (2026). The feature has
been rolling out through beta; confirm current status in the docs before committing a project to it.

## What it is

The server is the single source of truth; clients send only **inputs**. To hide latency, each client
**predicts** a few frames ahead of the last known server state, compares its prediction with the
authoritative state when it arrives, and on a **misprediction** rolls back to the server state and
resimulates forward, re-applying its inputs. Movement exploits (speed, fly, teleport) disappear because
clients never report positions.

## Setup (Workspace)

`AuthorityMode = Server` (automatically sets the rest): `NextGenerationReplication` on,
`PlayerScriptsUseInputActionSystem` on, `SignalBehavior = Deferred`, `UseFixedSimulation` on,
`StreamingEnabled` on.

## Rules for code

1. **Simulation sync**: put core logic in functions bound with `RunService:BindToSimulation(fn)` inside a
   ModuleScript that both a server Script and a client LocalScript require and initialize. These run on
   fixed steps and are re-run during resimulation.
2. **Only simulation-access APIs** (labelled "Simulation Access" in the API reference, e.g.
   `BasePart.CFrame`) can be used inside bound functions.
3. **Inputs**: clients influence the game only through Input Actions. `InputContext`s must be descendants
   of the `Player` (e.g. the server clones an `Inputs` folder into each player on join). Read
   `action:GetState()` for every player inside the simulation on both sides. Don't use
   `UserInputService` events in core simulation.
4. **State**: sync custom data via **attributes** on predicted instances, written only inside simulation
   callbacks. Replicated attributes: first 64 per instance, names ≤ 50 chars, string values ≤ 50 chars.
5. **Remote events** still work for discrete, non-simulation messages (score popups, purchases) but are
   not ordered relative to property/attribute replication.
6. **Prediction control**: Roblox predicts simulation-access properties near the local character by default;
   force it on/off with `RunService:SetPredictionMode(instance, mode)`.

```luau
--!strict
-- ReplicatedStorage/Simulation.luau — required by a server Script and a client LocalScript.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local Simulation = {}

function Simulation.initialize()
	RunService:BindToSimulation(function(deltaTime: number)
		for _, player in Players:GetPlayers() do
			local inputs = player:FindFirstChild("Inputs")
			local dash = inputs and inputs:FindFirstChild("Dash", true)
			if dash and dash:IsA("InputAction") and dash:GetState() == true then
				local character = player.Character
				local root = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
				if root then
					root:ApplyImpulse(root.CFrame.LookVector * root.AssemblyMass * 50 * deltaTime)
				end
			end
		end
	end)
end

return Simulation
```

## Techniques

- **Instance stitching**: create instances (`Instance.new`, `Clone`, `Instance.fromExisting`) inside a
  simulation callback from a module required on both sides; client and server derive the same GUID and
  the client's predicted instance is merged with the server's copy. Parent them within the same frame.
- **Position smoothing**: simulate an invisible object and render a massless, non-collidable visual
  copy that follows it with `TweenService:SmoothDamp` to hide correction snaps.
- **Animations**: don't cache `AnimationTrack`s (rollback invalidates them); each step, get the live
  track with `Animator:GetTrackByAnimationId(id)` or load it, and mirror animation logic on both sides.
- **Sounds/VFX**: play effects from predicted state carefully — they may need to be cancelled if the
  prediction is rolled back; trigger irreversible effects from confirmed (server) state.
- **Other players' inputs** can't be known in advance; design mechanics tolerant of small corrections
  (wind-ups, telegraphed attacks) and use smoothing.
- Debug with the **server authority visualizer** and tune the simulation radius.

Official templates: Racing, Soccer, and Laser Tag "Server Authority Template" games on Roblox.
