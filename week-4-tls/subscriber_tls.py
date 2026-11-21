import ssl
import json
import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion

TLS_CONFIG = {
    "ca_certs": "certs/ca.pem",
    "broker_host": "localhost",
    "broker_port": 8883,
}

TOPIC = "hydroficient/grandmarina/sensors/+/readings"


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected successfully over TLS!")
        client.subscribe(TOPIC)
        print(f"Subscribed to: {TOPIC}\n")
        print("Waiting for messages (Ctrl+C to stop)...\n")
    else:
        print(f"Connection failed (rc={rc})")


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        location = data.get("location", "unknown")
        pu = data.get("pressure_upstream", "?")
        pd = data.get("pressure_downstream", "?")
        fr = data.get("flow_rate", "?")
        cnt = data.get("counter", "?")
        print(f"[RECEIVED] {location}: pressure={pu}/{pd} PSI, flow={fr} gal/min (counter={cnt})")
    except Exception:
        print(f"[RECEIVED RAW] topic={msg.topic} payload={msg.payload!r}")


def on_disconnect(client, flags, userdata, rc, properties=None):
    if rc != 0:
        print(f"Unexpected disconnect (rc={rc})")


print("==================================================")
print("  GRAND MARINA HOTEL - Secure Subscriber")
print("  TLS-Encrypted MQTT Connection")
print("==================================================\n")

client = mqtt.Client(
    client_id="gm-secure-subscriber",
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
client.on_message = on_message
client.on_disconnect = on_disconnect

print(f"Configuring TLS with CA: {TLS_CONFIG['ca_certs']}")
print(f"Connecting to {TLS_CONFIG['broker_host']}:{TLS_CONFIG['broker_port']} with TLS...")

client.connect(TLS_CONFIG["broker_host"], TLS_CONFIG["broker_port"], keepalive=60)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\nStopping subscriber...")
finally:
    try:
        client.disconnect()
    except Exception:
        pass
    print("Subscriber stopped cleanly.")
