# Luau type system (new solver) — reference

Authoritative spec: <https://luau.org/typecheck>. Everything here type-checks under the new solver in `--!strict`.

## Modes

| Hot comment | Behavior |
| --- | --- |
| `--!nocheck` | No type errors reported. |
| `--!nonstrict` | Infers types, reports only definite errors. Unannotated values are `any`-ish. |
| `--!strict` | Full inference and checking. Use for all new modules. |

`Workspace.LuauTypeCheckMode` sets the default for scripts without a hot comment;
`Workspace.UseNewLuauTypeSolver` (a `RolloutState`) selects the solver. With Rojo + luau-lsp, set
`"luau-lsp.fflags.enableNewSolver": true` (or the equivalent in your editor) so editor and Studio agree.

## Building blocks

```luau
--!strict
type Id = string
type Maybe<T> = T? -- same as T | nil
type Vec = { x: number, y: number } -- table (record) type
type List = { number } -- array
type Map = { [string]: number } -- dictionary
type Callback = (player: Player, amount: number) -> boolean
type Varargs = (...number) -> () -- variadic, returns nothing
type Pair<K, V = string> = { key: K, value: V } -- generic with a default
type Shape = { kind: "circle", radius: number } | { kind: "rect", w: number, h: number } -- tagged union

local function area(shape: Shape): number
	if shape.kind == "circle" then
		return math.pi * shape.radius ^ 2 -- refined to the circle variant
	else
		return shape.w * shape.h
	end
end

local lookup: Map = { a = 1 }
local pair: Pair<number> = { key = 1, value = "one" }
print(area({ kind = "rect", w = 2, h = 3 }), lookup, pair)
```

- Tagged unions + `if x.kind == ...` give exhaustive, refined handling — prefer them over loose optional fields.
- Intersections `A & B` combine table types; overloaded function types are intersections of function types.

## Generics and type packs

```luau
--!strict
local function map<T, U>(list: { T }, fn: (T) -> U): { U }
	local out = table.create(#list)
	for i, v in list do
		out[i] = fn(v)
	end
	return out
end

local function wrap<A..., R...>(fn: (A...) -> R...): (A...) -> R...
	return function(...: A...): R...
		return fn(...)
	end
end

local names = map({ 1, 2, 3 }, function(n)
	return `#{n}`
end)
print(names, wrap(math.max)(1, 5))
```

`T...` is a type pack (a list of types), used for varargs and multiple returns.

## Refinement

```luau
--!strict
local function describe(value: unknown): string
	if typeof(value) == "Instance" then
		if value:IsA("BasePart") then
			return `part at {value.Position}` -- refined to BasePart
		end
		return value:GetFullName()
	elseif type(value) == "number" then
		return string.format("%.2f", value)
	end
	return "unknown"
end
print(describe(workspace))
```

- Use `unknown` (not `any`) for values you haven't validated: the checker forces you to refine.
- `assert(x, "msg")` refines `x` to non-nil after the call.
- `FindFirstChild` returns `Instance?`; use `FindFirstChildOfClass("Humanoid")` or `FindFirstChildWhichIsA`
  to get a typed result, or refine with `IsA`.

## Casts

`expr :: T` asserts a type. It's only allowed when the types are related (e.g. `Instance` → `Part`).
To force an unrelated cast, go through `any`: `(x :: any) :: T` — a code smell; prefer refinement.

## Read-only / write-only properties

```luau
--!strict
type Settings = { read version: number, volume: number }

local settings: Settings = { version = 2, volume = 0.5 }
settings.volume = 1 -- ok
-- settings.version = 3 -- type error: property is read-only
print(settings.version)
```

Pair with `table.freeze` for runtime immutability.

## Built-in type functions

`keyof<T>` (union of a table's key literals), `index<T, K>` (type of a property), `typeof(expr)`,
plus `rawkeyof`, `rawget`, `getmetatable`, `setmetatable` type functions.

```luau
--!strict
local DEFAULTS = { walkSpeed = 16, jumpPower = 50 }
type SettingName = keyof<typeof(DEFAULTS)> -- "walkSpeed" | "jumpPower"

local function get(name: SettingName): number
	return DEFAULTS[name]
end
print(get("walkSpeed"))
```

## User-defined type functions

Type functions run at analysis time and build types programmatically with the `types` library.

```luau
--!strict
type function Partial(t)
	local result = types.newtable()
	for key, prop in t:properties() do
		result:setproperty(key, types.optional(prop.read))
	end
	return result
end

type Stats = { health: number, mana: number }
local patch: Partial<Stats> = { mana = 10 }
print(patch)
```

Use sparingly: they improve library APIs but make code harder for teammates to read.

## Typing classes (OOP)

Pattern A — infer from the constructor (least boilerplate):

```luau
--!strict
local Account = {}
Account.__index = Account

type AccountData = { owner: Player, balance: number }
export type Account = typeof(setmetatable({} :: AccountData, Account))

function Account.new(owner: Player): Account
	return setmetatable({ owner = owner, balance = 0 }, Account)
end

function Account.deposit(self: Account, amount: number)
	assert(amount > 0, "amount must be positive")
	self.balance += amount
end

return Account
```

Pattern B — explicit interface (best for public library APIs; decouples the shape from the metatable):

```luau
--!strict
export type Timer = {
	start: (self: Timer) -> (),
	elapsed: (self: Timer) -> number,
}

local function newTimer(): Timer
	local startedAt = os.clock()
	local timer = {}
	function timer.start(_self: Timer)
		startedAt = os.clock()
	end
	function timer.elapsed(_self: Timer): number
		return os.clock() - startedAt
	end
	return timer
end

return newTimer
```

Inheritance: prefer composition (a field holding another object). If you must inherit, set the child
metatable's `__index` to the parent class and type the child as an intersection of both shapes.

## Common errors → fixes

| Error | Fix |
| --- | --- |
| `Value of type 'Instance?' could be nil` | Refine: `local x = parent:FindFirstChild("X"); if not x then return end`. |
| `Key 'Foo' not found in external type 'Instance'` | Refine with `IsA`, cast (`:: Folder`), or use a Rojo sourcemap so luau-lsp knows children. |
| `Type 'string' could not be converted into 'number'` | Convert explicitly (`tonumber(s)`) and handle `nil`. |
| `Unknown type used in + operation` | Annotate the parameter (`function f(a: number)`). |
| `Cannot add property 'x' to table` | Declare the field in the table type or constructor literal. |
| Types from a required module are `any` | The require path isn't resolvable statically: use instance paths or string requires, and a sourcemap with Rojo. |

## Migrating a codebase to strict

1. Enable the new solver; add `--!strict` file by file, starting with leaf modules (utilities, data).
2. Add `export type` for every module's public data shape; annotate function parameters and returns.
3. Replace `FindFirstChild` chains with typed accessors or validated lookups.
4. Treat remote payloads and DataStore data as `unknown` and write validators that return typed values.
5. Keep `any` only at explicit boundaries, with a comment explaining why.
