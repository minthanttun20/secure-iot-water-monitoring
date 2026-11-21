# SECURITY ASSESSMENT: Grand Marina Hotel Water Monitoring System

**Prepared for:** Marcus Webb, General Manager  
**Prepared by:** Min Thant Tun  
**Date:** 29 January 2026  

---

## Executive Summary

We assessed the security and performance of the Grand Marina water monitoring system after adding TLS encryption. Our testing shows that the system is now protected against eavesdropping and unauthorized access, while performance impact remains minimal. We recommend deploying the TLS-secured system into production, as it significantly improves security without affecting hotel operations or sensor responsiveness.

---

## Security Risks Addressed

### Before TLS
Without encryption, sensor data was transmitted in plain text. Anyone on the same network could:
* Read water pressure and flow data
* Identify device IDs and sensor locations
* Potentially infer usage patterns or system behavior

This creates risks to operational security, data confidentiality, and hotel reputation, especially if attackers or competitors gain access.

### After TLS
With TLS enabled:
* All sensor messages are encrypted
* Only trusted systems with valid certificates can connect
* Unauthorized listeners are blocked automatically

This ensures the system communicates only with verified infrastructure and prevents spying or impersonation.

---

## Performance Impact

| Metric | Without Security | With Security | Assessment |
| :--- | :--- | :--- | :--- |
| **Message Latency** | 1.12 ms | 1.31 ms | Acceptable |
| **System Capacity** | $\ge 50\text{ msg/sec}$ | $\ge 50\text{ msg/sec}$ | Meets requirements |

**What this means:** The added security introduces an average delay of $0.19\text{ ms}$, which is imperceptible for water sensors that report every few seconds. Hotel leak detection, alerts, and monitoring remain unaffected.

---

## Testing Evidence

We conducted four structured security experiments to validate the system:

1. **Eavesdropping Test**
   * **Without TLS:** Sensor messages were visible in plain text to unauthorized subscribers.
   * **With TLS:** Unauthorized listeners could not connect and saw no data.
   * **Result:** TLS successfully blocks eavesdropping.

2. **Certificate Validation Test**
   * **Correct certificates:** Connection succeeded.
   * **Wrong CA certificate:** Connection failed with a verification error.
   * **No certificate verification:** Connection succeeded (unsafe configuration).
   * **Result:** Certificate validation prevents connections to fake or malicious brokers.

3. **Latency Test**
   * **TLS OFF:** Average latency = $1.12\text{ ms}$
   * **TLS ON:** Average latency = $1.31\text{ ms}$
   * **Calculated TLS overhead:** 
     $$\frac{1.31 - 1.12}{1.12} \times 100 \approx 17\%$$
   * **Result:** The performance cost is small and acceptable for hotel operations.

4. **Capacity (Stress) Test**
   * System handled $10$, $25$, and $50$ messages per second with TLS enabled.
   * Performance remained stable under normal and emergency scenarios.
   * **Result:** The system meets Grand Marina’s current and peak load requirements.

---

## Recommendation

We strongly recommend deploying the TLS-secured water monitoring system. The security improvements significantly reduce operational and reputational risk, while the performance impact is negligible. The system is safe, reliable, and ready for real-world use.