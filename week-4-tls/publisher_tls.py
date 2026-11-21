import ssl
import time
import json
import random
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion

TLS_CONFIG = {
    "ca_certs": "certs/ca.pem",
    "broker_host": "localhost",
    "broker_port": 8883,
}

LOCATIONS = ["main-building", "pool-spa", "boiler-room"]
INTERVAL_SECONDS = 2


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected successfully over TLS!\n")
    else:
        print(f"Connection failed (rc={rc})")


def on_disconnect(client, flags, userdata, rc, properties=None):
    # rc=0 is normal disconnect; avoid scary messages
    if rc != 0:
        print(f"Unexpected disconnect (rc={rc})")


print("==================================================")
print("  GRAND MARINA HOTEL - Secure Publisher")
print("  TLS-Encrypted MQTT Connection")
print("==================================================\n")

client = mqtt.Client(
    client_id="gm-secure-publisher",
    callback_api_version=CallbackAPIVersion.VERSION2
)

client.tls_set(
    ca_certs=TLS_CONFIG["ca_certs"],
    certfile=None,
    keyfile=None,
    cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLS,
)

client.on_connect = on_connect
client.on_disconnect = on_disconnect

print(f"Configuring TLS with CA: {TLS_CONFIG['ca_certs']}")
print(f"Connecting to {TLS_CONFIG['broker_host']}:{TLS_CONFIG['broker_port']} with TLS...")

client.connect(TLS_CONFIG["broker_host"], TLS_CONFIG["broker_port"], keepalive=60)
client.loop_start()

print("Publishing sensor data (Ctrl+C to stop)...\n")

counter = 0

try:
    while True:
        for location in LOCATIONS:
            counter += 1
            topic = f"hydroficient/grandmarina/sensors/{location}/readings"

            payload = {
                "device_id": "GM-HYDROLOGIC-01",
                "location": location,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "counter": counter,
                "pressure_upstream": round(82 + random.uniform(-2, 2), 1),
                "pressure_downstream": round(76 + random.uniform(-2, 2), 1),
                "flow_rate": round(40 + random.uniform(-3, 3), 1),
            }

            client.publish(topic, json.dumps(payload), qos=0)
            print(f"[{location}] Published: pressure={payload['pressure_upstream']}/"
                  f"{payload['pressure_downstream']} PSI, flow={payload['flow_rate']} gal/min")

        time.sleep(INTERVAL_SECONDS)

except KeyboardInterrupt:
    print("\nStopping publisher...")

finally:
    # Clean shutdown (prevents Ctrl+C ugly errors)
    try:
        client.loop_stop()
        client.disconnect()
    except Exception:
        pass
    print("Publisher stopped cleanly.")
