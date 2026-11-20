# Section 1: Executive Summary

## What system is being protected & why it matters
This assessment focuses on the Hydroficient HYDROLOGIC water management system, which monitors and remotely controls water flow for the Main Building, Pool/Spa, and Kitchen/Laundry at The Grand Marina. The system directly controls physical water infrastructure, meaning a cyber incident can quickly turn into real-world damage, guest disruption, and major financial loss. This risk is proven by the recent $4.2 million water damage incident caused by a missed alert.

## Top 3 Critical Concerns (Plain Language)
1. An attacker could remotely shut off water to large parts of the hotel, disrupting guests and operations.
2. Leak alerts could be blocked or falsified, leading to another major flooding incident.
3. Stolen staff login credentials could give full system control, without needing advanced hacking skills.

## Priority Recommendation
**First priority:** Secure the dashboard and control functions by enforcing multi-factor authentication (MFA), strong credential policies, and login monitoring. This directly reduces the most dangerous and likely attack paths.

---

# Section 2: System Overview

## Major Components
* **HYDROLOGIC Devices (3):** Installed in the Main Building, Pool/Spa, and Kitchen/Laundry; measure water pressure/flow and execute shutoff commands.
* **Cloud Server & APIs:** Process sensor data, generate alerts, store logs.
* **MQTT Broker:** Transfers data and commands between devices and cloud.
* **Web Dashboard:** Used by staff to view data and control water flow remotely.
* **Data Types:** Sensor readings, leak alerts, control commands, credentials, usage data.

```text
+----------------------+
|  HYDROLOGIC Devices  |
|  (Main / Pool / KL)  |
|  - Flow & Pressure   |
|  - Leak Detection    |
+----------+-----------+
           |
           |  Sensor Data / Alerts (MQTT)
           v
+----------------------+
|     MQTT Broker      |
|  - Message Transport |
+----------+-----------+
           |
           |  Forward Data
           v
+----------------------+
|   Cloud Server / API |
|  - Process Alerts    |
|  - Store Logs        |
|  - Business Rules    |
+----------+-----------+
           |
           |  Display & Control
           v
+----------------------+
|   Web Dashboard      |
|  - View Readings     |
|  - View Alerts       |
|  - Issue Commands    |
+----------+-----------+
           |
           |  Control / Shutoff Commands
           v
+----------------------+
|   Cloud Server / API |
+----------+-----------+
           |
           |  Command Delivery (MQTT)
           v
+----------------------+
|  HYDROLOGIC Devices  |
|  - Gate Control      |
|  - Emergency Shutoff |
+----------------------+
```

---

# Section 3: Asset Inventory

List the key assets and their CIA priorities:

| Asset | Description | C Priority | I Priority | A Priority |
| :--- | :--- | :--- | :--- | :--- |
| **HYDROLOGIC Devices** | 3 flow management units | Medium | Critical | Critical |
| **Web Dashboard** | Operator monitoring interface | Critical | Critical | High |
| **Cloud API** | Device-to-cloud communication | Medium | Critical | Critical |
| **Remote Controls** | Gate adjustments, emergency shutoff | High | Critical | Critical |
| **Consumption Data** | Savings reports, billing records | Medium | Medium | Low |

---

# Section 4: STRIDE Analysis

## Component 1: HYDROLOGIC Devices

| Threat | Scenario | Likelihood | Impact | Risk |
| :--- | :--- | :--- | :--- | :--- |
| **Spoofing** | Attacker impersonates a device and sends fake readings | Medium | High | High |
| **Tampering** | Sensor data modified before reaching cloud | Low | High | Medium |
| **Repudiation** | Device actions not properly logged | Low | Medium | Medium |
| **Info Disclosure** | Traffic sniffed on internal network | Medium | Medium | Medium |
| **Denial of Service** | Device overwhelmed and stops reporting | Medium | High | High |
| **Elevation of Privilege** | Firmware exploit grants device control | Low | Critical | High |

## Component 2: Web Dashboard

| Threat | Scenario | Likelihood | Impact | Risk |
| :--- | :--- | :--- | :--- | :--- |
| **Spoofing** | Attacker sends a phishing email to hotel staff, captures dashboard credentials, and logs in as a legitimate operator. | High | Critical | Critical |
| **Tampering** | Attacker with dashboard access changes alert thresholds or disables notifications so real leaks are not flagged. | Medium | High | High |
| **Repudiation** | Dashboard lacks detailed audit logs, allowing an attacker to trigger a shutoff and deny responsibility later. | Medium | Medium | Medium |
| **Information Disclosure** | Attacker accesses dashboard data and views sensor readings, usage patterns, and operational schedules. | Medium | Medium | Medium |
| **Denial of Service** | Attacker repeatedly submits heavy dashboard requests or exploits a UI flaw, making the dashboard unavailable during an incident. | Medium | High | High |
| **Elevation of Privilege** | Attacker exploits weak role separation to escalate from read-only user to admin with control privileges. | Low | Critical | High |

## Component 3: Cloud API

| Threat | Scenario | Likelihood | Impact | Risk |
| :--- | :--- | :--- | :--- | :--- |
| **Spoofing** | Attacker uses stolen API keys or tokens to impersonate a trusted service and send commands to devices. | Medium | High | High |
| **Tampering** | Attacker modifies API requests in transit to alter sensor data or control messages. | Low | High | Medium |
| **Repudiation** | Insufficient API logging allows attackers to perform actions without clear attribution. | Medium | Medium | Medium |
| **Information Disclosure** | Misconfigured API exposes sensor data or credentials to unauthorized users. | Medium | Medium | Medium |
| **Denial of Service** | Attacker floods the API with requests, preventing devices and dashboard from communicating. | High | Critical | Critical |
| **Elevation of Privilege** | Attacker exploits an API authorization flaw to gain administrative access to system functions. | Low | Critical | High |

## Component 4: Remote Controls (Gate/Shutoff)

| Threat | Scenario | Likelihood | Impact | Risk |
| :--- | :--- | :--- | :--- | :--- |
| **Spoofing** | Attacker sends forged control commands pretending to be the cloud system, triggering valve actions. | Medium | Critical | High |
| **Tampering** | Control commands are altered in transit, causing incorrect gate positions or shutoff timing. | Low | Critical | High |
| **Repudiation** | No clear record of who issued a shutoff command, making incident investigation difficult. | Medium | High | Medium |
| **Information Disclosure** | Attacker observes control traffic and learns how and when shutoffs are triggered. | Low | Medium | Low |
| **Denial of Service** | Attacker blocks or delays control commands, preventing shutoff during a real leak. | Medium | Critical | Critical |
| **Elevation of Privilege** | Attacker gains unauthorized ability to issue emergency shutoff commands. | Low | Critical | High |

---

# Section 5: Risk Summary

## Critical Risks
* Dashboard credential compromise enabling remote shutoff
* MQTT broker denial of service causing loss of visibility
* Leak alerts being blocked or altered, leading to flooding and financial loss

## High Risks
* Fake sensor data misleading operators
* Replay of valid shutoff commands
* Insider misuse of access

## Medium Risks
* Passive data exposure
* Weak logging and accountability

---

# Section 6: Recommended Mitigations

| Risk | Proposed Mitigation | Implementation Complexity |
| :--- | :--- | :--- |
| **Dashboard credential compromise** | Enforce multi-factor authentication (MFA) for all dashboard users and disable password-only access | Low – configuration change |
| **Phishing of staff credentials** | Implement email security filtering, phishing detection, and regular staff awareness training | Medium – tooling + training |
| **Unauthorized dashboard access** | Enable login anomaly detection (new location/device alerts) and session timeouts | Low – configuration change |
| **MQTT broker denial of service** | Apply rate limiting, connection quotas, and network segmentation for the broker | Medium – infrastructure changes |
| **Device or cloud spoofing** | Use per-device authentication credentials and strict MQTT topic access control lists (ACLs) | Medium – system configuration |
| **Sensor or alert tampering** | Implement message signing and integrity verification between devices and cloud | Medium – protocol update |
| **Suppressed or missed leak alerts** | Add alert escalation rules (SMS/phone/email) and alert acknowledgment | Low – configuration change |