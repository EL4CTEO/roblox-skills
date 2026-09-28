# Verifying Roblox webhooks

When a webhook has a secret, Roblox sends header `roblox-signature: t=<timestamp>,v1=<signature>`.
Signature = Base64( HMAC-SHA256( key = secret, message = `<timestamp>.<raw JSON body>` ) ).
Reject requests whose signature doesn't match, and requests older than a few minutes (replay protection).
Use the **raw** request body bytes, not a re-serialized object.

## Node.js (Express)

```javascript
import crypto from "node:crypto";
import express from "express";

const app = express();
const SECRET = process.env.ROBLOX_WEBHOOK_SECRET;

app.post("/roblox-webhook", express.raw({ type: "application/json" }), (req, res) => {
  const header = req.get("roblox-signature") ?? "";
  const parts = Object.fromEntries(header.split(",").map((kv) => kv.split("=", 2)));
  const timestamp = parts.t;
  const signature = parts.v1;
  if (!timestamp || !signature) return res.sendStatus(401);

  const ageSeconds = Math.abs(Date.now() / 1000 - Number(timestamp));
  if (ageSeconds > 300) return res.sendStatus(401);

  const expected = crypto
    .createHmac("sha256", SECRET)
    .update(`${timestamp}.${req.body.toString("utf8")}`)
    .digest("base64");
  const ok =
    expected.length === signature.length &&
    crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(signature));
  if (!ok) return res.sendStatus(401);

  const event = JSON.parse(req.body.toString("utf8"));
  // Idempotency: store processed event IDs; Roblox retries failed deliveries and may send duplicates.
  console.log("webhook", event.EventType ?? event.eventType, event);
  res.sendStatus(200);
});

app.listen(3000);
```

## Python (Flask)

```python
import base64, hashlib, hmac, os, time
from flask import Flask, request, abort

app = Flask(__name__)
SECRET = os.environ["ROBLOX_WEBHOOK_SECRET"].encode()

@app.post("/roblox-webhook")
def roblox_webhook():
    header = request.headers.get("roblox-signature", "")
    parts = dict(p.split("=", 1) for p in header.split(",") if "=" in p)
    ts, sig = parts.get("t"), parts.get("v1")
    if not ts or not sig or abs(time.time() - int(ts)) > 300:
        abort(401)
    body = request.get_data(as_text=True)
    expected = base64.b64encode(hmac.new(SECRET, f"{ts}.{body}".encode(), hashlib.sha256).digest()).decode()
    if not hmac.compare_digest(expected, sig):
        abort(401)
    event = request.get_json()
    # handle event idempotently
    return "", 200
```

## Handling events

- **Right to erasure**: delete the user's data from every data store/key and any external storage; see
  automated RTBF in `roblox-data-stores` (preferred when keys follow static patterns).
- **Refunds**: optionally revoke the refunded item/currency; record abuse patterns.
- **Commerce order paid**: may be delivered more than once — deduplicate by order ID.
- Respond `2xx` quickly and process asynchronously; failed deliveries are retried.
