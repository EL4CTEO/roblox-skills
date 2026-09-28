# Luau standard library on Roblox — cheat sheet

Only libraries and functions available in Roblox are listed. Deprecated: `table.getn`, `table.foreach`,
`table.foreachi`, `getfenv`, `setfenv`, globals `wait`, `spawn`, `delay`, `ypcall`, `version`, `elapsedTime`.

## task

`spawn(fnOrThread, ...)`, `defer(fnOrThread, ...)`, `delay(seconds, fnOrThread, ...)`, `wait(seconds?)`,
`cancel(thread)`, `desynchronize()`, `synchronize()` (Parallel Luau only).

## table

| Function | Notes |
| --- | --- |
| `table.create(n, value?)` | Preallocate an array of `n` slots. |
| `table.insert(t, v)` / `table.insert(t, i, v)` | Append / insert (shifts). |
| `table.remove(t, i?)` | Remove (shifts). For unordered removal: swap with last, then remove last. |
| `table.find(t, v, init?)` | Linear search in an array; returns index or nil. |
| `table.clear(t)` | Empties in place, keeps capacity (good for reused buffers). |
| `table.clone(t)` | Shallow copy. Deep copy must be written manually. |
| `table.freeze(t)` / `table.isfrozen(t)` | Shallow immutability. |
| `table.move(a, i, j, k, b?)` | Bulk copy ranges. |
| `table.concat(t, sep?)` | Join strings — use for building large strings. |
| `table.sort(t, lt?)` | In-place, not stable. Comparator must be a strict weak ordering (`<`, never `<=`). |
| `table.pack(...)` / `table.unpack(t, i?, j?)` | `pack` sets `n` (handles nils). |

## string

`split(s, sep)`, `format` (`%d %s %q %.2f %x`), `find/match/gmatch/gsub` (Lua patterns, not regex),
`sub`, `rep`, `lower/upper`, `byte/char`, `pack/unpack/packsize` (binary), `len`, `reverse`.
Interpolation: `` `Hi {name}` `` (use `\{` for a literal brace). `utf8` library for Unicode:
`utf8.len`, `utf8.codes`, `utf8.char`, `utf8.offset`, and Roblox additions `utf8.graphemes`,
`utf8.nfcnormalize`, `utf8.nfdnormalize` (use graphemes when counting/truncating user-visible text).

## math

`clamp`, `round`, `sign`, `floor`, `ceil`, `abs`, `min/max`, `lerp(a, b, t)`, `map(x, inMin, inMax, outMin, outMax)`,
`noise(x, y?, z?)` (Perlin, returns about -1..1), `random(m?, n?)`, `isnan`, `isinf`, `isfinite`,
`huge`, `pi`, `tau`. Prefer `Random.new(seed)` objects (`:NextInteger`, `:NextNumber`, `:Shuffle`) over
global `math.random` for reproducible or per-system RNG.

## buffer

Fixed-size mutable byte arrays. `create(size)`, `fromstring`, `tostring`, `len`, `copy`, `fill`,
`read/write` + `i8 u8 i16 u16 i32 u32 f32 f64`, `readstring/writestring(b, offset, str, count?)`,
`readbits/writebits(b, bitOffset, bitCount, value)`. Little-endian. Buffers can be sent through remotes
and stored in DataStores (serialized), and are the fastest way to pack network data.

## vector

`vector.create(x, y, z)`, `zero`, `one`, `magnitude`, `normalize`, `cross`, `dot`, `angle(a, b, axis?)`,
`floor`, `ceil`, `abs`, `sign`, `clamp`, `lerp`, `max`, `min`. Operates on the same immutable 3-component
value type as `Vector3`, with faster, native-codegen-friendly calls.

## bit32

`band`, `bor`, `bxor`, `bnot`, `lshift`, `rshift`, `arshift`, `extract`, `replace`, `btest`, `countlz`, `countrz`, `byteswap`.

## coroutine

`create`, `resume`, `yield`, `wrap`, `status`, `running`, `isyieldable`, `close`. Use coroutines for
generators/state machines; use `task.spawn`/`task.defer` to run code concurrently (errors inside a
`coroutine.resume` are returned, not reported to Output, and are easy to lose).

## os / time

`os.clock()` (high-res CPU time, benchmarking), `os.time()` (UTC seconds), `os.date(fmt, t)`,
`os.difftime`. Roblox datatypes: `DateTime.now()`, `DateTime.fromUnixTimestamp`, `:ToIsoDate()`,
`:FormatLocalTime(fmt, locale)`. Synced server clock: `workspace:GetServerTimeNow()`.

## debug

`traceback(msg?, level?)`, `info(level|fn, "slnaf")`, `profilebegin(label)` / `profileend()` (MicroProfiler
labels), `setmemorycategory(name)` / `resetmemorycategory()` (Developer Console memory tags),
`dumpcodesize()` (native codegen size in Studio).

## Roblox globals

`game`, `workspace`, `script`, `plugin` (plugins only), `shared` (avoid: untyped global table — use
modules), `typeof`, `require`, `settings()`, `UserSettings()`, `warn`, `print`, `error`, `tick` (avoid).
Datatypes: `Vector3`, `Vector2`, `CFrame`, `Color3`, `UDim`, `UDim2`, `Rect`, `NumberRange`,
`NumberSequence`, `ColorSequence`, `BrickColor`, `Enum`, `Instance`, `RaycastParams`, `OverlapParams`,
`TweenInfo`, `Random`, `DateTime`, `Font`, `Content`, `Path2DControlPoint`, `SharedTable`.
