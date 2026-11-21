# Imports

The script imports:

- **paho.mqtt.client** → to communicate with the MQTT broker
- **json** → to convert sensor readings into JSON format
- **random** → to add realistic variation to sensor values
- **time** → to control the publishing interval
- **datetime** and **timezone** → to generate ISO 8601 UTC timestamps

---

# WaterSensorMQTT Class

This class represents a simulated **HYDROLOGIC water sensor**.

## `__init__`

- Stores the device ID and location
- Initializes a counter that increments with each reading
- Connects to the MQTT broker and starts the background network loop
- Defines the MQTT topic where readings will be published
- Sets base pressure and flow values used to generate realistic readings

## `get_reading()`

This method generates a single sensor reading:

- Increments the counter
- Creates a timestamp in ISO 8601 UTC format
- Generates pressure and flow values with small random variations
- Returns all values as a Python dictionary

## `publish_reading()`

This method:

- Calls `get_reading()` to generate new sensor data
- Publishes the reading to the MQTT topic as a JSON message
- Uses QoS 0 to represent an insecure, best-effort delivery
- Returns the published reading so it can be displayed

## `run_continuous()`

This method:

- Prints startup information (device ID, location, topic, interval)
- Continuously publishes readings at the specified interval
- Displays each reading in a human-readable format
- Gracefully stops the MQTT client when the user presses **Ctrl+C**

---

# `main()` Function

The `main()` function:

- Defines the device ID, location, and publishing interval
- Creates an instance of the **WaterSensorMQTT** class
- Repeatedly publishes readings every 2 seconds
- Handles clean shutdown when the program is interrupted

---

# Imports and Configuration

The script imports:

- **paho.mqtt.client** → to communicate with the MQTT broker
- **json** → to parse incoming sensor messages
- **datetime** → to display the dashboard connection time

The broker address, port, and subscription topic are defined at the top.  
The dashboard subscribes to **hydroficient/grandmarina/#**, which allows it to receive all sensor data, alerts, and status messages for the Grand Marina.

---

# Functions

## `print_header()`

- Prints a dashboard banner when the client connects
- Includes the dashboard title and the current connection time
- Makes it clear when monitoring started

## `extract_location()`

- Extracts the building location from the MQTT topic
- Parses the topic structure to display which area (e.g., main building) the data is coming from
- Avoids relying solely on the message payload

## `on_connect()`

- Runs when the dashboard connects to the broker
- If successful:
  - Prints the dashboard header
  - Subscribes to the configured topic using QoS 0
- If failed:
  - Displays an error message

## `on_message()`

Handles every incoming MQTT message:

- Decodes the message payload from bytes to text
- Attempts to parse the payload as JSON
- Safely ignores and logs non-JSON messages
- Extracts relevant fields: device ID, timestamp, counter, pressure, and flow
- Calculates pressure differential if both pressure values are valid
- Displays all information in a structured, human-readable format

---

# `main()` Function

The `main()` function:

- Creates the MQTT client
- Registers the connection and message callbacks
- Connects to the broker
- Starts the network loop with `loop_forever()`
- Keeps the dashboard running continuously to receive live updates
