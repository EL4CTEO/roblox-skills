# Physics recipes

## CFrame cookbook

```luau
--!strict
local origin = CFrame.new(0, 5, 0)

local lookAt = CFrame.lookAt(Vector3.new(0, 5, 0), Vector3.new(10, 5, 10)) -- position facing a target
local rotated = origin * CFrame.Angles(0, math.rad(90), 0) -- rotate in local space
local worldRotated = CFrame.Angles(0, math.rad(90), 0) * origin -- rotate around world origin
local offset = origin * CFrame.new(0, 0, -5) -- 5 studs "forward" (LookVector is -Z)
local relative = origin:ToObjectSpace(lookAt) -- lookAt expressed relative to origin
local back = origin:ToWorldSpace(relative) -- == lookAt
local halfway = origin:Lerp(lookAt, 0.5)
local rx, ry, rz = lookAt:ToOrientation() -- radians (Y-X-Z order like Orientation)
local flat = CFrame.fromMatrix(Vector3.zero, Vector3.xAxis, Vector3.yAxis) -- from basis vectors

print(rotated, worldRotated, offset, back, halfway, rx, ry, rz, flat)
print(lookAt.LookVector, lookAt.RightVector, lookAt.UpVector, lookAt.Position)
```

- Compose right-to-left in world space, left-to-right in local space: `a * b` applies `b` in `a`'s space.
- Use `PivotTo`/`GetPivot` for models; `part.CFrame` for single parts.

## Projectiles

Pick by speed and precision:
1. **Hitscan** (instant): one server-validated `workspace:Raycast` — rifles, lasers.
2. **Simulated** (visible travel, drop): step a ray each frame; no physics parts needed.
3. **Physical** parts: only for slow, physics-interactive objects (grenades); set ownership deliberately.

```luau
--!strict
local RunService = game:GetService("RunService")

local GRAVITY = Vector3.new(0, -workspace.Gravity, 0)

local function fireProjectile(origin: Vector3, velocity: Vector3, params: RaycastParams, onHit: (RaycastResult) -> ())
	local position = origin
	local currentVelocity = velocity
	local travelled = 0
	local connection: RBXScriptConnection
	connection = RunService.Heartbeat:Connect(function(deltaTime)
		local step = currentVelocity * deltaTime + 0.5 * GRAVITY * deltaTime * deltaTime
		local result = workspace:Raycast(position, step, params)
		if result then
			connection:Disconnect()
			onHit(result)
			return
		end
		position += step
		currentVelocity += GRAVITY * deltaTime
		travelled += step.Magnitude
		if travelled > 1000 then
			connection:Disconnect() -- max range
		end
	end)
end

return fireProjectile
```

Clients render the bullet visuals locally (object pool of tracer parts or Beams); the server runs the
same stepping (or validates the client's reported hit — see `roblox-security`).

## Hover / follow with AlignPosition + AlignOrientation

```luau
--!strict
local function makeFollower(part: BasePart, target: BasePart)
	local attachment = Instance.new("Attachment")
	attachment.Parent = part

	local align = Instance.new("AlignPosition")
	align.Mode = Enum.PositionAlignmentMode.OneAttachment
	align.Attachment0 = attachment
	align.MaxForce = part.AssemblyMass * workspace.Gravity * 4
	align.Responsiveness = 20
	align.Parent = part

	local orient = Instance.new("AlignOrientation")
	orient.Mode = Enum.OrientationAlignmentMode.OneAttachment
	orient.Attachment0 = attachment
	orient.Responsiveness = 20
	orient.Parent = part

	return function()
		align.Position = target.Position + Vector3.new(0, 4, 0)
		orient.CFrame = target.CFrame
	end
end

return makeFollower
```

## Simple car (constraint-based)

- Chassis part (root) + 4 wheel parts (cylinders), each joined with a `CylindricalConstraint` (or
  `HingeConstraint` for non-steering wheels) whose `ActuatorType = Motor`; set `AngularVelocity` and
  `MotorMaxTorque` from the throttle. Steering: a `HingeConstraint` servo on the front wheel mounts
  (`ActuatorType = Servo`, `TargetAngle`).
- Suspension: `SpringConstraint` (`Stiffness`, `Damping`, `FreeLength`) or `CylindricalConstraint` limits.
- Read input from `VehicleSeat.ThrottleFloat`/`SteerFloat` (the integer `Throttle`/`Steer` are deprecated)
  or Input Actions; give the driver network ownership (`chassis:SetNetworkOwner(driver)`) for responsive
  handling, and validate speed on the server — or use server authority.

## Explosion without the Explosion instance's side effects

```luau
--!strict
local function blast(center: Vector3, radius: number, maxDamage: number)
	local params = OverlapParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	local hitHumanoids: { [Humanoid]: boolean } = {}
	for _, part in workspace:GetPartBoundsInRadius(center, radius, params) do
		local model = part:FindFirstAncestorOfClass("Model")
		local humanoid = model and model:FindFirstChildOfClass("Humanoid")
		if humanoid and not hitHumanoids[humanoid] then
			hitHumanoids[humanoid] = true
			local distance = (part.Position - center).Magnitude
			humanoid:TakeDamage(maxDamage * (1 - math.clamp(distance / radius, 0, 1)))
		elseif not part.Anchored then
			local direction = (part.Position - center).Unit
			part:ApplyImpulse(direction * part.AssemblyMass * 60)
		end
	end
end

return blast
```
