# Workshop Verification Rules

Workshop evidence is attached to the reusable component or procedure that was actually tested. It must never silently promote every related vehicle to exact-vehicle verified.

## Display levels

1. `workshop_verified_exact` — a successful event matches manufacturer, model, generation, year/configuration and operation.
2. `workshop_verified_related` — a successful event exists for the same shared component on another compatible vehicle.
3. `source_verified` — supported by a named manufacturer, tool maker or trusted technical source.
4. `provisional` — plausible but not yet sufficiently proven.
5. `unverified` — unknown or awaiting evidence.

The compiler preserves raw component evidence. The app decides whether an event is exact or related by comparing the selected vehicle with the event vehicle.

## Required job record

```json
{
  "id": "job-2026-07-22-example",
  "date": "2026-07-22",
  "result": "success",
  "vehicle": {
    "manufacturer": "Skoda",
    "model": "Octavia",
    "generation": "5E",
    "year": 2017,
    "market": "UK",
    "steering": "RHD",
    "vin_masked": null,
    "configuration": "MQB blade key"
  },
  "operation": "add_key",
  "tool": {
    "manufacturer": "Autel",
    "model": "IM508S",
    "software_version": null,
    "adapter": "XP400 Pro"
  },
  "working_key_present": true,
  "key_type": "ID88 MQB",
  "duration_minutes": null,
  "notes": "Example only — replace with a real workshop result before marking verified.",
  "evidence_refs": []
}
```

## Safety rules

- A failed or partial event remains in history; it must not be deleted to improve confidence.
- Tool model, software version and adapters should be recorded where known.
- AKL, add-key and spare-key are separate operations.
- Model-specific exceptions override shared compatibility.
- Unknown data remains `null` or `unverified`.
- VINs must be masked or omitted.
