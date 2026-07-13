# Database Schema

**Version:** 1.0  
**Status:** Approved  
**Last updated:** 2026-07-14

## Purpose

This document defines the simplified JSON structure used by the Locksmith Companion Database and app.

## Folder Layout

```text
database/vehicles/<manufacturer>/<model>/
├── manifest.json
├── models.json
├── procedures.json
├── modules.json
├── wiring.json
├── service_functions.json
├── notes.json
└── photos.json
```

Manufacturer-level files:

```text
database/vehicles/<manufacturer>/
├── manifest.json
├── platforms.json
└── key_systems.json
```

## Search Structure

The app search path is:

`manufacturer badge → model badge → UK year range → ignition/security variant`

Underlying platform names must not replace the badge name.

## Core Vehicle Record

```json
{
  "record_id": "ford_fiesta_2008_2012_keyed",
  "vehicle": {
    "make": "Ford",
    "model": "Fiesta",
    "year_from": 2008,
    "year_to": 2012,
    "market": "UK",
    "drive_side": "RHD",
    "ignition_type": "keyed",
    "variant": "Keyed ignition"
  },
  "key_information": {
    "key_type": "remote key",
    "blade_profile": "HU101",
    "emergency_blade": null,
    "transponder_type": "verification_required",
    "frequency_mhz": "433.92",
    "battery": "CR2032",
    "buttons": "3"
  },
  "security": {
    "family": "Ford PATS",
    "security_generation": "FORD_PATS_BCM",
    "platform": "Ford",
    "programming_module": "BCM",
    "programming_route": "OBD",
    "security_access": "verification_required",
    "online_requirement": "not_required",
    "fdrs_requirement": "not_required",
    "gateway_requirement": "not_applicable"
  },
  "operations": {
    "add_key": {},
    "all_keys_lost": {},
    "remote_programming": null,
    "parameter_reset": null
  },
  "tools": {},
  "modules": {},
  "notes": {}
}
```

## Controlled Status Values

Use only:

- `verified`
- `verification_required`
- `vin_or_build_dependent`
- `supported`
- `unsupported`
- `required`
- `not_required`
- `not_applicable`
- `unknown`

## Operation Object

```json
{
  "status": "supported",
  "method": "OBD",
  "online_requirement": "not_required",
  "required_equipment": [],
  "warnings": [],
  "evidence_status": "verified"
}
```

## Tool Support Object

Tool support must be operation-specific:

```json
{
  "autel_im508s": {
    "add_key": "supported",
    "all_keys_lost": "verification_required",
    "parameter_reset": "not_applicable",
    "required_cable": null,
    "software_version_checked": null,
    "evidence_date": "2026-07-14",
    "notes": ""
  }
}
```

Do not use a single general `supported: true` value for all functions.

## Module Object

```json
{
  "name": "Body Control Module",
  "abbreviation": "BCM",
  "location_rhd": "verification_required",
  "programming_relevance": "Controls PATS key programming",
  "removal_required": false
}
```

## Notes Object

Keep notes concise and job-relevant:

```json
{
  "warnings": [],
  "job_notes": [],
  "shared_platform_note": null
}
```

## Verification Metadata

Verification may be stored in the model data or a dedicated audit record, but must include:

- last verified date;
- field status;
- sources;
- unresolved conflicts;
- reviewer/workshop evidence where applicable.

## Null and Missing Values

- Use `null` when the field is applicable but not yet populated.
- Use `not_applicable` when the field does not apply.
- Use `unknown` only after research found no reliable answer.
- Never fill a missing fact with an assumption.

## Versioning

- Schema-breaking changes increment the major schema version.
- New optional fields increment the minor version.
- Data corrections increment manufacturer/model data versions.
- Manifest hashes and update timestamps must change whenever released data changes.

## Validation Requirements

Before release:

- JSON must parse;
- required keys must exist;
- year ranges must be valid;
- controlled values must be recognised;
- duplicate record IDs must fail validation;
- tool support must be operation-specific;
- model manifests must reference existing files;
- the app must display records without legacy fallbacks.
