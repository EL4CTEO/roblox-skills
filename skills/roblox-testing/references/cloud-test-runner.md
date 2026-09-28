# Running tests in the cloud with Open Cloud Luau Execution

Runs a Luau script inside a real Roblox server for a specific place version. Good for CI of code that
needs the engine (instances, services, physics). Not available: players/characters, and DataStores
behave like a live server of that universe (use a dedicated test universe).

## One-time setup

1. Create a **test universe** with a test place (never run tests against production data).
2. Creator Dashboard → Open Cloud → API Keys: create a key with
   `universe.place.luau-execution-session:write` for the test universe (plus `universe-places` write
   to upload versions). Store it as a CI secret.

## Test script executed by the task

```luau
--!strict
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Jest = require(ReplicatedStorage.DevPackages.Jest) :: any
local root = ReplicatedStorage.Shared

local status, result = Jest.runCLI(root, { ci = true, verbose = true }, { root }):awaitStatus()
if status ~= "Resolved" then
	error(`Jest failed to run: {result}`)
end
local failed = result.results.numFailedTests + result.results.numFailedTestSuites
if failed > 0 then
	error(`{failed} failing tests/suites`) -- makes the task FAILED
end
return result.results.numPassedTests
```

## Driver (bash + curl + jq)

```bash
#!/usr/bin/env bash
set -euo pipefail
: "${ROBLOX_API_KEY:?}" "${UNIVERSE_ID:?}" "${PLACE_ID:?}"
API=https://apis.roblox.com

# 1. Upload the built test place as a new saved version.
VERSION=$(curl -sf -X POST \
  "$API/universes/v1/$UNIVERSE_ID/places/$PLACE_ID/versions?versionType=Saved" \
  -H "x-api-key: $ROBLOX_API_KEY" -H "Content-Type: application/octet-stream" \
  --data-binary @test.rbxl | jq -r .versionNumber)

# 2. Start the task.
TASK=$(jq -n --rawfile script scripts/run-tests.luau '{script: $script, timeout: "300s"}' |
  curl -sf -X POST \
    "$API/cloud/v2/universes/$UNIVERSE_ID/places/$PLACE_ID/versions/$VERSION/luau-execution-session-tasks" \
    -H "x-api-key: $ROBLOX_API_KEY" -H "Content-Type: application/json" --data @- | jq -r .path)

# 3. Poll until done.
while true; do
  RESPONSE=$(curl -sf "$API/cloud/v2/$TASK" -H "x-api-key: $ROBLOX_API_KEY")
  STATE=$(echo "$RESPONSE" | jq -r .state)
  case "$STATE" in
    COMPLETE) echo "$RESPONSE" | jq .output; break ;;
    FAILED|CANCELLED) echo "$RESPONSE" | jq .error; FAILED=1; break ;;
    *) sleep 5 ;;
  esac
done

# 4. Print the script's log output.
curl -sf "$API/cloud/v2/$TASK/logs" -H "x-api-key: $ROBLOX_API_KEY" | jq -r '.luauExecutionSessionTaskLogs[]?.messages[]?'
exit "${FAILED:-0}"
```

- Tasks default to a 5-minute timeout; the rate limit is about 5 task creations per minute per API key owner.
- Check the Open Cloud reference for the current response field names if `jq` paths return null.
