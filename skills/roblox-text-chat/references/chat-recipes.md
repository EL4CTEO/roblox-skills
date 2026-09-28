# Chat recipes

## Proximity chat (server)

```luau
--!strict
local Players = game:GetService("Players")
local TextChatService = game:GetService("TextChatService")

local RANGE = 50
local channels = TextChatService:WaitForChild("TextChannels")
local general = channels:WaitForChild("RBXGeneral") :: TextChannel

local function positionOf(userId: number): Vector3?
	local player = Players:GetPlayerByUserId(userId)
	local character = player and player.Character
	return character and character:GetPivot().Position
end

general.ShouldDeliverCallback = function(message: TextChatMessage, target: TextSource): boolean
	local source = message.TextSource
	if not source or source.UserId == target.UserId then
		return true -- always show senders their own message
	end
	local from, to = positionOf(source.UserId), positionOf(target.UserId)
	return from ~= nil and to ~= nil and (from - to).Magnitude <= RANGE
end
```

## Team or party channel (server)

```luau
--!strict
local TextChatService = game:GetService("TextChatService")

local function createPartyChannel(partyId: string, members: { Player }): TextChannel
	local channel = Instance.new("TextChannel")
	channel.Name = `Party_{partyId}`
	channel.Parent = TextChatService:WaitForChild("TextChannels")
	for _, member in members do
		local ok, source = pcall(function()
			return channel:AddUserAsync(member.UserId)
		end)
		if not ok or not source then
			warn(`could not add {member.Name}`)
		end
	end
	return channel -- clients send with channel:SendAsync(text); Destroy() when the party ends
end

return createPartyChannel
```

Teams: the built-in `/team` command and team channels exist when `CreateDefaultCommands`/
`CreateDefaultTextChannels` are on and `Teams` are set up.

## Rate-limited bulletin board (server)

```luau
--!strict
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TextService = game:GetService("TextService")

local COOLDOWN = 60 -- at least 1 minute for player-editable public text
local MAX_LENGTH = 140

local postNote = Instance.new("RemoteEvent")
postNote.Name = "PostNote"
postNote.Parent = ReplicatedStorage

local lastPost: { [Player]: number } = {}

postNote.OnServerEvent:Connect(function(player, text: unknown)
	if typeof(text) ~= "string" or #text == 0 or #text > MAX_LENGTH or utf8.len(text) == nil then
		return
	end
	local now = os.clock()
	if lastPost[player] and now - lastPost[player] < COOLDOWN then
		return
	end
	lastPost[player] = now
	local ok, filtered = pcall(function()
		return TextService:FilterStringAsync(text, player.UserId):GetNonChatStringForBroadcastAsync()
	end)
	if ok then
		postNote:FireAllClients(player.UserId, filtered)
	end
end)

Players.PlayerRemoving:Connect(function(player)
	lastPost[player] = nil
end)
```

## Custom chat UI

Set `ChatWindowConfiguration.Enabled = false` and `ChatInputBarConfiguration.Enabled = false`, then:
- Send: `(TextChatService.TextChannels.RBXGeneral :: TextChannel):SendAsync(textBox.Text)`.
- Receive: `TextChatService.MessageReceived:Connect(function(message) ... end)`; render
  `message.PrefixText` and `message.Text` (already filtered). Use `message.MessageId` to replace the
  sender's local pending message when the server-processed version arrives.
- Keep bubble chat via `BubbleChatConfiguration` or `TextChatService.OnBubbleAdded`.

## Migrating from legacy Chat

| Legacy | TextChatService |
| --- | --- |
| `Chat:Chat(part, text)` bubbles | `TextChatService:DisplayBubble(part, text)` (client) |
| ChatService speakers/channels | `TextChannel` + `AddUserAsync`; permissions via `TextSource.CanSend` |
| Extra data (tags, colors) on speakers | `OnIncomingMessage` returning `TextChatMessageProperties` (`PrefixText`, `Text`) with rich text |
| `Chat:FilterStringAsync` | `TextService:FilterStringAsync` |
| Custom commands via message hooks | `TextChatCommand` instances (`PrimaryAlias`, `SecondaryAlias`, `Triggered`) |
