# Rewarded video ads, commerce products, Premium and Roblox Plus

## Rewarded video ads (AdService)

Requirements: creator 13+ and ID-verified, public game with ≥ 2k monthly unique visitors, serving
enabled in **Creator Hub → Monetization → Ads → Settings**, and a developer product as the reward.

Client — show the button only when an ad is available (check right before showing):

```luau
--!strict
local AdService = game:GetService("AdService")

local function isAdAvailable(): boolean
	local ok, result = pcall(function()
		return AdService:GetAdAvailabilityNowAsync(Enum.AdFormat.RewardedVideo)
	end)
	return ok and result.AdAvailabilityResult == Enum.AdAvailabilityResult.IsAvailable
end

print(isAdAvailable())
```

Server — play the ad; the reward arrives through `ProcessReceipt` like any developer product:

```luau
--!strict
local AdService = game:GetService("AdService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local REWARD_PRODUCT_ID = 1919753834 -- developer product in this universe
local requestAd = Instance.new("RemoteEvent")
requestAd.Name = "RequestRewardedAd"
requestAd.Parent = ReplicatedStorage

local watching: { [Player]: boolean } = {}

requestAd.OnServerEvent:Connect(function(player)
	if watching[player] then
		return
	end
	watching[player] = true
	local ok, result = pcall(function()
		local reward = AdService:CreateAdRewardFromDevProductId(REWARD_PRODUCT_ID)
		return AdService:ShowRewardedVideoAdAsync(player, reward)
	end)
	watching[player] = nil
	requestAd:FireClient(player, ok, result) -- Enum.ShowAdResult.ShowCompleted on success
end)
```

- Protect the character during the ad (lobby/safe zone or pause damage).
- Clearly label "Watch an ad to get X"; rewards can't be random.

## Commerce products (real-world goods)

Eligible creators can sell physical products (e.g. imported from Shopify) with bundled digital
benefits. Prompt with `MarketplaceService:PromptCommerceProductPurchase(player, commerceProductId)`
(a string ID); bundled developer-product benefits are granted through `ProcessReceipt`, avatar items
are granted by Roblox. Check eligibility requirements in the Commerce products docs before building.

## Premium and Roblox Plus

- `player.HasRobloxSubscription` is `true` for players with an active Roblox subscription (use it for
  subscriber perks; `Player.MembershipType` is deprecated). Engagement-based payouts reward subscriber
  playtime automatically — make perks cosmetic/convenience, never pay-to-win.
- **Roblox Plus** subscribers get 10–20% off eligible purchases (Roblox covers the discount; your
  earnings don't drop), free paid private servers (you're still compensated), and free Robux transfers.
- `MarketplaceService:PromptRobloxSubscriptionPurchase(player)` prompts a Roblox Plus sign-up and
  earns a referral payout. `PromptPremiumPurchase` is deprecated.

## Private servers

Enable and price in Creator Dashboard. Detect with `game.PrivateServerId ~= ""` and
`game.PrivateServerOwnerId` (`VIPServerId`/`VIPServerOwnerId` are deprecated). Reserved servers
(`TeleportService:ReserveServerAsync`) also have a non-empty `PrivateServerId` but owner id `0`.

## Analytics for monetization

Log currency sources/sinks with `AnalyticsService:LogEconomyEvent` and purchase funnels with
`LogFunnelStepEvent` (see `roblox-analytics-liveops`) so you can see which offers convert.
