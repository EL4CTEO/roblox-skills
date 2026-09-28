# Inventory, equipment, shop, pets

## Item catalog (server-authoritative data)

```luau
--!strict
-- ReplicatedStorage/Shared/Items.luau — shared so clients can render names/icons/prices.
-- The server still re-reads prices from here; never from client messages.
export type Item = {
	id: string,
	name: string,
	price: number?, -- nil = not sold in the shop
	maxStack: number,
	toolTemplate: string?, -- name of a Tool in ServerStorage.Tools
}

local Items: { [string]: Item } = {
	Sword = { id = "Sword", name = "Iron Sword", price = 100, maxStack = 1, toolTemplate = "Sword" },
	Potion = { id = "Potion", name = "Health Potion", price = 25, maxStack = 20 },
}

return table.freeze(Items)
```

## Inventory service (server)

```luau
--!strict
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")

local Items = require(ReplicatedStorage.Shared.Items)

type Inventory = { [string]: number }

local inventories: { [Player]: Inventory } = {} -- point this at profile.Data.inventory on load
local changed = Instance.new("RemoteEvent")
changed.Name = "InventoryChanged"
changed.Parent = ReplicatedStorage

local InventoryService = {}

function InventoryService.load(player: Player, saved: Inventory)
	inventories[player] = saved
	changed:FireClient(player, "snapshot", saved)
end

function InventoryService.count(player: Player, itemId: string): number
	local inventory = inventories[player]
	return inventory and inventory[itemId] or 0
end

function InventoryService.add(player: Player, itemId: string, amount: number): boolean
	local inventory = inventories[player]
	local item = Items[itemId]
	if not inventory or not item or amount <= 0 then
		return false
	end
	local current = inventory[itemId] or 0
	if current + amount > item.maxStack then
		return false
	end
	inventory[itemId] = current + amount
	changed:FireClient(player, "delta", itemId, inventory[itemId])
	return true
end

function InventoryService.remove(player: Player, itemId: string, amount: number): boolean
	local inventory = inventories[player]
	local current = inventory and inventory[itemId] or 0
	if not inventory or amount <= 0 or current < amount then
		return false
	end
	local remaining = current - amount
	inventory[itemId] = if remaining > 0 then remaining else nil
	changed:FireClient(player, "delta", itemId, remaining)
	return true
end

-- Equip = clone the Tool template into the backpack; the tool's behavior lives in a tagged service.
function InventoryService.equip(player: Player, itemId: string): boolean
	local item = Items[itemId]
	local backpack = player:FindFirstChildOfClass("Backpack")
	if not item or not item.toolTemplate or not backpack or InventoryService.count(player, itemId) < 1 then
		return false
	end
	local template = ServerStorage:WaitForChild("Tools"):FindFirstChild(item.toolTemplate)
	if not template or backpack:FindFirstChild(template.Name) then
		return false
	end
	template:Clone().Parent = backpack
	return true
end

Players.PlayerRemoving:Connect(function(player)
	inventories[player] = nil
end)

return InventoryService
```

Tools in the backpack are lost on respawn unless re-granted: re-equip owned items on `CharacterAdded`
(or clone into `player.StarterGear` so Roblox restores them).

## Shop purchase with soft currency (server)

```luau
--!strict
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Items = require(ReplicatedStorage.Shared.Items)
local CurrencyService = require(ServerScriptService.Server.Services.CurrencyService)
local InventoryService = require(ServerScriptService.Server.Services.InventoryService)

local buy = Instance.new("RemoteFunction")
buy.Name = "BuyItem"
buy.Parent = ReplicatedStorage

local lastBuy: { [Player]: number } = {}

buy.OnServerInvoke = function(player: Player, itemId: unknown): (boolean, string)
	local now = os.clock()
	if now - (lastBuy[player] or 0) < 0.3 then
		return false, "Too fast"
	end
	lastBuy[player] = now

	if typeof(itemId) ~= "string" then
		return false, "Invalid item"
	end
	local item = Items[itemId]
	if not item or not item.price then
		return false, "Not for sale"
	end
	if InventoryService.count(player, itemId) >= item.maxStack then
		return false, "Inventory full"
	end
	if not CurrencyService.spend(player, item.price, `Shop:{itemId}`) then
		return false, "Not enough coins"
	end
	if not InventoryService.add(player, itemId, 1) then
		CurrencyService.add(player, item.price, "Refund") -- keep the operation atomic
		return false, "Could not add item"
	end
	return true, "Purchased"
end

Players.PlayerRemoving:Connect(function(player)
	lastBuy[player] = nil
end)
```

Robux purchases go through developer products and `ProcessReceipt` instead (`roblox-monetization`).

## Pets that follow the player

- Server spawns the pet model (cosmetic ownership is server-side data), sets
  `pet.PrimaryPart:SetNetworkOwner(player)` so the owner's client moves it smoothly, and replicates
  `PetOwner` as an attribute.
- The owner's client moves the pet each frame toward an offset behind the character with
  `AlignPosition`/`AlignOrientation` (see `roblox-physics` recipes) — or all clients animate every pet
  locally from the owner's position (no physics, cheapest for many pets).
- Hatching/random pets bought with Robux or Robux-bought currency are **paid random items**: disclose
  odds and respect `PolicyService` restrictions (`roblox-monetization`).
