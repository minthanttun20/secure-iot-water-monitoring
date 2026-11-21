import json
from datetime import datetime

import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"
BROKER_PORT = 1883

TOPIC = "hydroficient/grandmarina/#"

try:
    MQTT_CLIENT_ARGS = {"callback_api_version": mqtt.CallbackAPIVersion.VERSION1}
except AttributeError:
    MQTT_CLIENT_ARGS = {}

def print_header():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("=" * 60)
    print("  GRAND MARINA WATER MONITORING DASHBOARD")
    print(f"  Connected at: {now}")
    print("=" * 60)
    print()

def extract_location(topic: str) -> str:
    # hydroficient/grandmarina/sensors/<location>/readings
    parts = topic.split("/")
    if len(parts) >= 5 and parts[2] == "sensors":
        return parts[3]
    return "unknown"

def on_connect(client, userdata, flags, rc):
    # rc=0 means success
    if rc == 0:
        print_header()
        client.subscribe(TOPIC, qos=0)
    else:
        print(f"Failed to connect (rc={rc})")

def on_message(client, userdata, msg):
    topic = msg.topic
    raw = msg.payload.decode("utf-8", errors="replace")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(f"[Non-JSON message] topic={topic} payload={raw}")
        return

    location = extract_location(topic)
    device_id = data.get("device_id", "unknown")
    ts = data.get("timestamp", "unknown")
    counter = data.get("counter", "unknown")

    up = data.get("pressure_upstream")
    down = data.get("pressure_downstream")
    flow = data.get("flow_rate")

    # compute differential safely
    diff = None
    if isinstance(up, (int, float)) and isinstance(down, (int, float)):
        diff = round(up - down, 1)

    print("─" * 40)
    print(f"  Location:  {location}")
    print(f"  Device ID: {device_id}")
    print(f"  Time:      {ts}")
    print(f"  Count:     #{counter}")
    print("─" * 40)
    if up is not None:
        print(f"  Pressure (upstream):    {up} PSI")
    if down is not None:
        print(f"  Pressure (downstream):  {down} PSI")
    if flow is not None:
        print(f"  Flow rate:              {flow} gal/min")
    if diff is not None:
        print(f"  Pressure differential:  {diff} PSI")
    print()


def main():
    client = mqtt.Client(client_id="grandmarina-dashboard", clean_session=True)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)

    # run the network loop forever (subscriber needs it)
    client.loop_forever()

if __name__ == "__main__":
    main()
