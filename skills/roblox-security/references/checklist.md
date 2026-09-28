# Security review checklist

Run through this for any code that handles client input, currency, items, or player data.

## Remotes

- [ ] Every `OnServerEvent`/`OnServerInvoke` validates **every** argument's type with `typeof`.
- [ ] Numbers checked with `math.isfinite` before range checks (NaN/inf bypass comparisons).
- [ ] Strings length-capped and UTF-8 validated (`utf8.len(s) ~= nil`) before use or saving.
- [ ] Tables: expected shape only, size-capped, no trusting of nested fields; no reading "Instance-like" tables.
- [ ] Instances checked with `IsA` **and** `IsDescendantOf(trustedContainer)`.
- [ ] Per-player rate limit; per-player state cleared on `PlayerRemoving`.
- [ ] Handler checks context: alive, distance, cooldown, ownership, permissions, game phase.
- [ ] No handler grants rewards based on client-reported outcomes (damage dealt, score, kills, coins).
- [ ] No `RemoteFunction:InvokeClient` anywhere.
- [ ] Remotes that relay to other clients (`FireAllClients` on client request) validate and rate-limit,
      and clamp what other clients receive (effect positions near the sender, bounded sizes).
- [ ] No remote loads assets or requires modules by client-supplied IDs/paths.

## Physics and movement

- [ ] Gameplay-critical unanchored parts are server-owned (`SetNetworkOwner(nil)`) or anchored.
- [ ] Interactables (`ProximityPrompt`, `ClickDetector`) are not in client-ownable assemblies.
- [ ] Movement-sensitive rewards (races, obbies) validate checkpoints in order with plausible timing.
- [ ] Server authority considered for competitive games.

## Economy and data

- [ ] Prices, drop rates, stats defined only in server modules.
- [ ] Currency changes happen in one server module with invariant checks (never negative, capped).
- [ ] Trades are atomic (validate both → commit both → save both; revert on failure; lock during trade).
- [ ] Developer products granted only in `ProcessReceipt`, idempotently by `PurchaseId`.
- [ ] Session locking for player data (ProfileStore or equivalent) to prevent cross-server duplication.

## Confidentiality and access

- [ ] No server logic or secrets in `ReplicatedStorage`, `ReplicatedFirst`, `StarterPlayer`, `StarterGui`, `Workspace`.
- [ ] API keys stored as experience Secrets and read with `HttpService:GetSecret`.
- [ ] Restricted places: "Secure within universe only" access control + server-side eligibility check, default deny.
- [ ] Admin commands check `player.UserId` against a server-side list (or group role via
      `GroupService:GetRolesInGroupAsync`), never `player.Name`, never a client flag.

## Common vulnerable patterns

```luau nocheck
-- ❌ Client decides the outcome
Remote.OnServerEvent:Connect(function(player, amount)
	player.leaderstats.Coins.Value += amount
end)

-- ❌ NaN passes both checks
if typeof(amount) == "number" and amount > 0 and amount <= balance then end

-- ❌ Trusting a client-provided "item" table or ReplicatedStorage value object for the price
BuyItem.OnServerInvoke = function(player, item) return charge(player, item.Price.Value) end

-- ❌ Relay without validation: any client can make everyone's screen flash anywhere
Cast.OnServerEvent:Connect(function(player, position) Cast:FireAllClients(position) end)

-- ❌ Admin check by name or by client-sent flag
if player.Name == "Owner" or isAdminFlagFromClient then end
```

```luau
--!strict
-- ✅ Server owns the numbers; client only asks
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ITEMS: { [string]: { price: number } } = { Sword = { price = 100 } }
local balances: { [Player]: number } = {}

local buyItem = Instance.new("RemoteFunction")
buyItem.Name = "BuyItem"
buyItem.Parent = ReplicatedStorage

buyItem.OnServerInvoke = function(player: Player, itemId: unknown): boolean
	if typeof(itemId) ~= "string" then
		return false
	end
	local item = ITEMS[itemId]
	local balance = balances[player] or 0
	if not item or balance < item.price then
		return false
	end
	balances[player] = balance - item.price
	-- grant item in the server-side inventory here
	return true
end
```
