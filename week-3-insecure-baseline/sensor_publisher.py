import paho.mqtt.client as mqtt
import json
import random
import time
from datetime import datetime, timezone


try:
    MQTT_CLIENT_ARGS = {"callback_api_version": mqtt.CallbackAPIVersion.VERSION1}
except AttributeError:
    MQTT_CLIENT_ARGS = {}

class WaterSensorMQTT:
    """
    A water sensor that publishes readings to MQTT.
    """

    def __init__(self, device_id, location, broker="localhost", port=1883):
        self.device_id = device_id
        self.location = location
        self.counter = 0

        # MQTT setup
        self.client = mqtt.Client()
        self.client.connect(broker, port)
        self.client.loop_start()

        # Topic for this sensor
        self.topic = f"hydroficient/grandmarina/sensors/{self.location}/readings"

        # Base values for realistic variation
        self.base_pressure_up = 82
        self.base_pressure_down = 76
        self.base_flow = 40

    def get_reading(self):
        """Generate a sensor reading with realistic variation."""
        self.counter += 1
        return {
            "device_id": self.device_id,  # identity
            "location": self.location,    # context (optional but recommended)
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "counter": self.counter,
            "pressure_upstream": round(self.base_pressure_up + random.uniform(-2, 2), 1),
            "pressure_downstream": round(self.base_pressure_down + random.uniform(-2, 2), 1),
            "flow_rate": round(self.base_flow + random.uniform(-3, 3), 1),
        }

    def publish_reading(self):
        """Generate a reading and publish it to MQTT."""
        reading = self.get_reading()
        self.client.publish(self.topic, json.dumps(reading), qos=0)
        return reading

    def run_continuous(self, interval=2):
        """Publish readings continuously at the specified interval."""
        print(f"Starting device: {self.device_id}")
        print(f"Location: {self.location}")
        print(f"Publishing to: {self.topic}")
        print(f"Interval: {interval} seconds")
        print("-" * 40)

        try:
            while True:
                reading = self.publish_reading()
                print(f"[{reading['counter']}] Pressure: {reading['pressure_upstream']}/{reading['pressure_downstream']} PSI, Flow: {reading['flow_rate']} gal/min")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nSensor stopped.")
            self.client.loop_stop()
            self.client.disconnect()

def main():
    device_id = "GM-HYDROLOGIC-01"
    location = "main-building"
    interval = 2

    sensor = WaterSensorMQTT(
        device_id=device_id,
        location=location,
        broker="localhost",
        port=1883
    )

    print(f"Starting device: {device_id}")
    print(f"Location: {location}")
    print(f"Publishing to: hydroficient/grandmarina/sensors/{location}/readings")
    print(f"Interval: {interval} seconds")
    print("----------------------------------------")

    try:
        while True:
            reading = sensor.publish_reading()
            print(
                f"[{reading['counter']}] "
                f"Pressure: {reading['pressure_upstream']}/"
                f"{reading['pressure_downstream']} PSI, "
                f"Flow: {reading['flow_rate']} gal/min"
            )
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nSensor stopped.")
        sensor.client.loop_stop()
        sensor.client.disconnect()


if __name__ == "__main__":
    main()
