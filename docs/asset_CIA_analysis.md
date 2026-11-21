# Asset CIA Analysis

| Asset | Confidentiality (1-5) | Integrity (1-5) | Availability (1-5) | Justification (Why did you rate it this way?) |
| :--- | :---: | :---: | :---: | :--- |
| **Pressure/flow readings** | 2 | 5 | 4 | Readings are not sensitive; leaking does not strongly impact operations, but if readings are altered, the system may fail to detect leaks or pressure issues. Operators need real-time readings to monitor the system, and downtime delays response to problems. |
| **Gate control commands** | 4 | 5 | 5 | If an attacker gets commands, they could understand system behavior or plan an attack. Modified commands could open or close gates incorrectly, causing water damage or service disruption. Commands must always be executable to control water flow during normal and emergency situations. |
| **Emergency shutoff capability** | 3 | 5 | 5 | Knowledge of how the shutoff works could be misused, though it is less critical than integrity and availability. A shutoff failure might cause serious damage or safety risks. The shutoff must be available all the time, especially during emergencies. |
| **Dashboard login credentials** | 5 | 5 | 4 | Leaked credentials allow attackers full system access, and unauthorized changes to credentials could lock out legitimate users or grant unauthorized access. Operators need access to manage the system, though short downtime is less severe than compromise. |
| **Consumption/savings data** | 4 | 4 | 3 | Usage data may reveal occupancy patterns or user behavior, and incorrect data leads to wrong billing, reports, or savings analysis. Temporary unavailability is inconvenient but may not cause immediate harm. |
| **Leak detection alerts** | 3 | 5 | 5 | Alerts are not highly sensitive but indicate vulnerabilities if exposed. False or missing alerts can result in undetected leaks and serious damage. Alerts must be delivered immediately to allow a fast response. |

---

# Attack Mapping

For each attack type you learned, identify one specific scenario at The Grand Marina:

| Attack Type | Specific Scenario | Which Asset Is Targeted | CIA Impact |
| :--- | :--- | :--- | :--- |
| **Eavesdropping** | Attacker on guest Wi-Fi captures MQTT traffic between HYDROLOGIC devices and the broker. | Pressure/flow sensor data | Confidentiality |
| **Spoofing** | Attacker pretends to be a HYDROLOGIC device and sends fake sensor data to the MQTT broker. | Sensor readings / alerts | Integrity |
| **Replay Attack** | Attacker records a valid gate control message and replays it later to trigger valve actions. | Gate control commands | Integrity and Availability |
| **Man-in-the-Middle** | Attacker intercepts and alters MQTT messages between devices and the broker. | Leak detection alerts | Integrity and Confidentiality |
| **Denial of Service** | Attacker floods the MQTT broker, blocking devices from sending data. | MQTT broker / sensor data | Availability |
| **Unauthorized Access** | Attacker logs into the dashboard using stolen credentials. | Dashboard credentials / controls | Confidentiality, Integrity, and Availability |

---

# Priority Ranking

Based on your analysis, rank the six attacks from most dangerous to least dangerous for The Grand Marina:

1. **Unauthorized Access**  
   It gives the attacker full control of the dashboard, allowing them to view data, change settings, and issue gate or shutoff commands—impacting confidentiality, integrity, and availability.
2. **Man-in-the-Middle**  
   Very dangerous as it allows silent interception and modification of sensor data and alerts, causing operators to trust false information and make incorrect decisions.
3. **Replay Attack**  
   High impact because replayed control or shutoff commands can trigger unexpected valve actions, disrupting water supply or causing damage.
4. **Spoofing**  
   Moderate danger since fake sensor data or alerts can mislead the system, though device authentication may reduce how easily this attack succeeds.
5. **Denial of Service**  
   Disruptive but usually temporary; it affects availability but does not directly compromise data integrity or confidentiality.
6. **Eavesdropping**  
   Least dangerous because it mainly exposes data without altering system behavior or causing immediate operational impact.