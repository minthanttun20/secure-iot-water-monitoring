# Week 4 — TLS Encryption

Adds TLS so traffic is encrypted and clients can verify the broker's identity. Includes a test tool for measuring the performance cost.

## What it does

- `generate_certs.py` creates a private Certificate Authority (CA) and a server certificate for the broker (`ca.pem`, `server.pem`, `server-key.pem`) and verifies the chain.
- `mosquitto_tls.conf` runs the broker on port 8883 with TLS.
- `publisher_tls.py` and `subscriber_tls.py` are the week 3 sensor and dashboard, now connecting over TLS and verifying the broker's certificate. The publisher simulates three locations (main building, pool/spa, boiler room).
- `experiment_runner.py` is a test tool with several modes: connection test, publish test, latency test, stress test, and wrong-CA test.

## Files

| File | Purpose |
|------|---------|
| `generate_certs.py` | Creates CA + server certificate in `certs/` |
| `mosquitto_tls.conf` | Broker config with TLS on port 8883 |
| `publisher_tls.py` | TLS sensor publisher (3 locations) |
| `subscriber_tls.py` | TLS subscriber |
| `experiment_runner.py` | Connection, latency, stress and wrong-CA tests |

> **Note:** `certs/` is never committed (it contains private keys). Week 5's `generate_client_certs.py` supersedes this script and also creates client certificates. Start week 5 from an empty `certs/` folder.

## How to run

From the repository root:

```bash
python week-4-tls/generate_certs.py
mosquitto -c week-4-tls/mosquitto_tls.conf -v
python week-4-tls/subscriber_tls.py
python week-4-tls/publisher_tls.py
```

Experiments:

```bash
python week-4-tls/experiment_runner.py --mode connect --tls on
python week-4-tls/experiment_runner.py --mode latency --tls on  --count 50
python week-4-tls/experiment_runner.py --mode latency --tls off --count 50   # needs the week 3 broker on 1883
python week-4-tls/experiment_runner.py --mode stress  --tls on  --rate 25 --duration 30
python week-4-tls/experiment_runner.py --mode generate-wrong-ca
python week-4-tls/experiment_runner.py --mode test-wrong-ca                  # should FAIL to connect
```

## Results

> ⚠️ *Fill in with your own measurements:*

| Test | TLS off | TLS on |
|------|---------|--------|
| Average latency | [ ] ms | [ ] ms |
| Std deviation | [ ] ms | [ ] ms |
| Stress test success rate | [ ] % | [ ] % |
| Wrong CA | n/a | Rejected ✔ |

## What TLS fixes, and what it doesn't

| Fixed | Still open |
|-------|-----------|
| Eavesdropping: traffic is encrypted | Anyone holding the CA certificate can still connect (`require_certificate false`) |
| Broker impersonation: clients verify the server cert | `allow_anonymous true`: no client identity |

## Next

Week 5 requires every client to present its own certificate (mutual TLS).
