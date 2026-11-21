# Week 3 — Insecure Baseline

A simulated water sensor publishes pressure and flow readings over plain MQTT, and a console dashboard displays them. **This is intentionally insecure.** It is the "before" picture that the rest of the project fixes.

## What it does

- `sensor_publisher.py` simulates a HYDROLOGIC water sensor (`WaterSensorMQTT` class). Every 2 seconds it publishes JSON with upstream/downstream pressure and flow rate, with small random variation around base values.
- `dashboard_subscriber.py` subscribes to `hydroficient/grandmarina/#`, parses each message, and prints a readable dashboard with location, device, timestamp, counter, pressures, flow and the pressure differential.
- `CODE_WALKTHROUGH.md` is a line-by-line explanation of both scripts.

## Files

| File | Purpose |
|------|---------|
| `sensor_publisher.py` | Simulated sensor, publishes to `hydroficient/grandmarina/sensors/<location>/readings` |
| `dashboard_subscriber.py` | Console dashboard subscriber |
| `mosquitto_insecure.conf` | Broker config: plaintext, anonymous |
| `CODE_WALKTHROUGH.md` | Explanation of the code |

`mosquitto_insecure.conf` should contain:

```
listener 1883 localhost
allow_anonymous true
log_type all
log_dest stdout
```

## How to run

Run from the repository root, each in its own terminal:

```bash
mosquitto -c week-3-insecure-baseline/mosquitto_insecure.conf -v
python week-3-insecure-baseline/dashboard_subscriber.py
python week-3-insecure-baseline/sensor_publisher.py
```

## Message format

```json
{
  "device_id": "GM-HYDROLOGIC-01",
  "location": "main-building",
  "timestamp": "2026-02-20T10:15:00+00:00",
  "counter": 12,
  "pressure_upstream": 82.4,
  "pressure_downstream": 75.9,
  "flow_rate": 41.3
}
```

## Why this is insecure

| Weakness | Consequence |
|----------|-------------|
| Plaintext on port 1883 | Anyone on the network can read every reading |
| `allow_anonymous true` | Anyone can connect and publish fake data |
| No message authentication | The dashboard cannot tell real data from forged data |
| QoS 0 | Best-effort delivery, no guarantee |

> 📸 *Add a screenshot of the dashboard output here, and ideally a `mosquitto_sub` or Wireshark capture showing readable plaintext.*

## Next

Week 4 encrypts the connection with TLS.
