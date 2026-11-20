# Part 1: Topic Hierarchy

```text
hydroficient/
└── grandmarina/
    ├── sensors/
    │   ├── main-building/
    │   │   └── readings/
    │   │       ├── pressure_upstream
    │   │       ├── pressure_downstream
    │   │       └── flow_rate
    │   ├── pool-spa-wing/
    │   │   └── readings/
    │   │       ├── pressure_upstream
    │   │       ├── pressure_downstream
    │   │       └── flow_rate
    │   └── kitchen-laundry/
    │       └── readings/
    │           ├── pressure_upstream
    │           ├── pressure_downstream
    │           └── flow_rate
    ├── commands/
    │   ├── emergency/
    │   │   └── shutoff
    │   ├── gate/
    │   │   └── adjust
    │   └── threshold/
    │       └── update
    ├── alerts/
    │   ├── critical/
    │   │   └── leak-detected
    │   └── warning/
    │       ├── pressure-anomaly
    │       └── flow-anomaly
    └── status/
        ├── heartbeat
        └── connection
```

## Design Notes

I organized sensors by building area (Main Building, Pool/Spa Wing, and Kitchen/Laundry) to reflect how facility operators manage the Grand Marina. Operators are responsible for specific areas rather than individual device IDs, so this structure makes it easy to monitor all water systems in a given location.

Alerts are separated into critical and warning levels because they require different operational responses. Critical alerts, such as leak detection, require immediate action to prevent damage and service disruption, while warning alerts like pressure or flow anomalies indicate potential issues that should be investigated. This separation also supports different Quality of Service (QoS) levels, with critical alerts using higher reliability.

Commands are grouped under a dedicated `commands/` namespace to clearly separate control actions from sensor data. These include emergency shutoff, gate adjustments, and threshold updates. These commands are sensitive and should be tightly controlled, as misuse, especially of emergency shutoff, could disrupt hotel operations or cause safety issues.

---

# Part 2: Security Reflection

**1. What happens if someone subscribes to `hydroficient/grandmarina/#`?**
They would receive all data under the Grand Marina, including sensor readings, alerts, status updates, and potentially command messages. This level of access should only be available to trusted systems or administrators, not regular users.

**2. What sensitive information could they see?**
They could see water usage patterns that reveal hotel operations, such as when the pool or spa is heavily used or when the kitchen and laundry are most active. Device names and topics also reveal physical locations inside the hotel. By watching timestamps over time, they could learn daily routines and busy periods.

**3. What actions could they take if they could also publish to command topics?**
If someone could publish to command topics, they could trigger an emergency shutoff or change gate settings. This could disrupt water supply to rooms, pools, or kitchens, affecting guests and potentially causing safety or service issues.