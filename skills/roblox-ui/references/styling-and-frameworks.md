# UI styling and declarative frameworks

## StyleSheet selectors

| Selector | Matches | Example |
| --- | --- | --- |
| `Class` | GuiObject/UIComponent class | `"TextButton"`, `"UICorner"` |
| `.Tag` | CollectionService tag | `".Primary"` |
| `#Name` | Instance name | `"#CloseButton"` |
| `:State` | `Enum.GuiState` (`Hover`, `Press`, `NonInteractable`, `Idle`) | `"TextButton:Hover"` |
| `@Query` | Active `StyleQuery`, or built-ins: `@PreferredInput{Gamepad,KeyboardAndMouse,Touch}`, `@ViewportDisplaySize{Small,Medium,Large}`, `@PreferredTextSize{Medium,Large,Larger,Largest}`, `@ReducedMotionEnabled{True,False}` | `"@ViewportDisplaySizeSmall"` |
| `::Class` | Pseudo-instance modifier (adds e.g. a UICorner without inserting one) | `"TextButton::UICorner"` |
| `A > B`, `A B` | Child / descendant combinators | `".Container > ImageLabel"` |

Property values can reference tokens with `$TokenName`. One `StyleSheet` applies per tree via a `StyleLink`.

## Tokens, theme, and rules in code

```luau
--!strict
local Players = game:GetService("Players")

local screenGui = Instance.new("ScreenGui")
screenGui.ResetOnSpawn = false

-- Design tokens live as attributes.
local tokens = Instance.new("StyleSheet")
tokens.Name = "Tokens"
tokens:SetAttribute("Primary", Color3.fromHex("3B82F6"))
tokens:SetAttribute("PrimaryHover", Color3.fromHex("60A5FA"))
tokens:SetAttribute("Radius", UDim.new(0, 8))

-- The sheet linked to the UI derives the tokens.
local sheet = Instance.new("StyleSheet")
sheet.Name = "AppStyle"
local derive = Instance.new("StyleDerive")
derive.StyleSheet = tokens
derive.Parent = sheet

local button = Instance.new("StyleRule")
button.Selector = ".Primary"
button:SetProperties({
	BackgroundColor3 = "$Primary",
	TextColor3 = Color3.new(1, 1, 1),
	AutoButtonColor = false,
})
button.Parent = sheet

local hover = Instance.new("StyleRule")
hover.Selector = ".Primary:Hover"
hover:SetProperty("BackgroundColor3", "$PrimaryHover")
hover.Parent = sheet

local corner = Instance.new("StyleRule")
corner.Selector = ".Primary::UICorner"
corner:SetProperty("CornerRadius", "$Radius")
corner.Parent = sheet

local link = Instance.new("StyleLink")
link.StyleSheet = sheet
link.Parent = screenGui

local buy = Instance.new("TextButton")
buy.Text = "Buy"
buy.Size = UDim2.fromOffset(160, 48)
buy:AddTag("Primary")
buy.Parent = screenGui

tokens.Parent = screenGui
sheet.Parent = screenGui
screenGui.Parent = Players.LocalPlayer:WaitForChild("PlayerGui")
```

Themes: create `LightTheme`/`DarkTheme` sheets that define the same token names, and point the
app sheet's `StyleDerive.StyleSheet` at the active theme to switch at runtime.

## React (jsdotlua/react)

```luau
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

local React = require(ReplicatedStorage.Packages.React)
local ReactRoblox = require(ReplicatedStorage.Packages.ReactRoblox)

local function Counter(props: { label: string })
	local count, setCount = React.useState(0)
	return React.createElement("TextButton", {
		Size = UDim2.fromOffset(200, 50),
		Text = `{props.label}: {count}`,
		[React.Event.Activated] = function()
			setCount(count + 1)
		end,
	})
end

local container = Instance.new("ScreenGui")
container.Parent = Players.LocalPlayer:WaitForChild("PlayerGui")
local root = ReactRoblox.createRoot(container)
root:render(React.createElement(Counter, { label = "Clicks" }))
```

- Keep game state outside components (a store/controller); pass data down, emit intents up.
- Use `React.useEffect` cleanup to disconnect Roblox signals.

## Fusion (0.3 style)

```luau
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Fusion = require(ReplicatedStorage.Packages.Fusion)

local scope = Fusion.scoped(Fusion)
local count = scope:Value(0)

local button = scope:New("TextButton")({
	Size = UDim2.fromOffset(200, 50),
	Text = scope:Computed(function(use)
		return `Clicks: {use(count)}`
	end),
	[Fusion.OnEvent("Activated")] = function()
		count:set(Fusion.peek(count) + 1)
	end,
})

-- scope:doCleanup() destroys everything created in this scope.
```

APIs differ between major versions of these libraries: check the installed version's docs.
