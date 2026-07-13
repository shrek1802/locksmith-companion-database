# Locksmith Companion Database — Development Standard

**Version:** 1.0  
**Status:** Approved  
**Last updated:** 2026-07-14  
**Scope:** UK-market auto-locksmith key programming database

## 1. Purpose

This document defines the mandatory workflow for researching, structuring, verifying, generating and releasing vehicle data for the Locksmith Companion Database.

The database is designed for professional UK auto locksmiths. It must prioritise fast vehicle identification, correct security-system selection and reliable tool-compatibility information.

## 2. Core Principles

1. Vehicles are found by the badge name shown on the vehicle and the applicable UK year range.
2. Technical records are split by security generation, not by facelift alone.
3. Shared-platform vehicles remain under their displayed brand and model name, while the underlying security architecture is recorded inside the record.
4. UK-market and right-hand-drive information takes priority.
5. Only key-programming-relevant information is stored.
6. No field is marked verified without recorded evidence.
7. JSON is not generated until the manufacturer has passed the required audit phases.
8. The app is a compatibility and job-reference tool, not a replacement for the connected programmer's guided procedure.

## 3. Mandatory Manufacturer Workflow

Every manufacturer must pass the following phases in order.

### Phase 0 — Manufacturer Preparation

Before technical data is entered:

- Build the complete UK model inventory.
- Use the exact badge name shown on the vehicle.
- Confirm UK sale years.
- Identify shared-platform or rebadged vehicles.
- Identify keyed, passive-start and other ignition variants.
- Record missing, rare and low-priority models rather than silently excluding them.

**Exit requirement:** the UK model inventory is complete enough to begin the security-generation audit.

### Phase 1 — Security-Generation Audit

For each badge/model, determine whether separate records are required because of changes to:

- immobiliser generation;
- BCM, IPC, KESSY, CAS, FEM, BDC, BSI, UCH or equivalent architecture;
- keyed versus passive-start system;
- transponder technology;
- programming route;
- OBD, EEPROM or bench requirements;
- online-security access;
- FDRS, SFD, SGW or equivalent gateway requirements;
- platform origin or underlying manufacturer.

A cosmetic facelift alone does not justify a new record unless the locksmith-relevant system changed.

**Exit requirement:** all proposed year and ignition splits are evidence-based and locked for technical research.

### Phase 2 — Technical Verification

Verify the simplified key-programming fields for every locked record:

- badge name and UK year range;
- ignition type;
- underlying platform and security family;
- key type;
- blade or emergency blade;
- transponder;
- UK remote frequency;
- key battery where confirmed;
- Add Key support;
- All Keys Lost support;
- programming route;
- online, FDRS, SFD or SGW requirement;
- required cable, adaptor or bypass;
- individual tool compatibility by operation;
- programming-relevant module locations for UK RHD vehicles;
- concise warnings and job notes.

Each field is verified independently. A record may contain a mixture of verified and held fields.

**Exit requirement:** no safety- or job-critical field is presented as fact without sufficient evidence.

### Phase 3 — JSON Generation

JSON may be generated only after:

- record splits are locked;
- the applicable technical fields have been approved;
- field names match `Docs/DATABASE_SCHEMA.md`;
- validation scripts pass;
- manufacturer and model manifests are updated;
- changed versions are incremented.

Generated JSON must not contain unsupported legacy fields merely for compatibility.

### Phase 4 — App Validation

Before a manufacturer is marked complete:

- download the manufacturer through the app's normal update process;
- confirm manufacturer, model, year and ignition navigation;
- confirm simplified fields display correctly;
- confirm empty fields do not create broken or misleading cards;
- confirm tool compatibility and warnings are readable on Android;
- confirm offline reload after the initial download;
- confirm the previous saved database remains usable after a failed update.

## 4. Record-Splitting Rule

Create a separate record whenever a locksmith could select the wrong key, tool function or programming route by using one combined record.

Typical split triggers include:

- keyed ignition versus passive start;
- different transponder families;
- security-module generation change;
- OBD support changing to online, bench or EEPROM;
- FDRS or gateway security becoming mandatory;
- a platform changing to another manufacturer's architecture;
- a confirmed build-date or VIN breakpoint.

Do not invent exact breakpoints. Use `verification_required` until evidence supports the split.

## 5. Shared-Platform Policy

The app search structure remains:

`Manufacturer badge → Model badge → UK year range → ignition/security variant`

Examples:

- Ford Ka remains under Ford Ka even when the security architecture is Fiat CODE.
- Ford Galaxy remains under Ford Galaxy even when an early generation uses Volkswagen architecture.
- Ford Transit Connect remains under Ford Transit Connect when the current generation uses Volkswagen MQB architecture.

The underlying platform must be visible in the record but must not replace the badge search name.

## 6. Verification States

Use only these controlled states:

- `verified` — evidence meets the project standard;
- `verification_required` — evidence is incomplete, conflicting or too broad;
- `vin_or_build_dependent` — the variation is real but the exact breakpoint must be checked for the vehicle;
- `unsupported` — confirmed not supported;
- `not_applicable` — the field does not apply;
- `unknown` — no reliable evidence found.

Avoid vague terms such as "probably", "usually", "generally" or "should work" in released vehicle data.

## 7. Evidence Standard

Evidence must follow `Docs/EVIDENCE_HIERARCHY.md`.

A field is normally approved when supported by one of the following:

- an official manufacturer source;
- official tool-manufacturer coverage for the exact function;
- two independent professional sources that agree;
- clear documented workshop evidence.

Retail key listings may support physical key details but must not, by themselves, prove programming capability.

Forum or social-media evidence may identify an issue for further checking but is not normally sufficient for final approval.

## 8. Tool Compatibility Standard

Tool compatibility must be recorded by exact operation, not as one general tick.

Minimum operations where applicable:

- Add Key;
- All Keys Lost;
- erase keys;
- parameter reset or module synchronisation;
- security-data read;
- EEPROM or bench read/write;
- remote generation only.

A key generator is not to be marked as a vehicle programmer unless it performs the immobiliser programming operation.

Tool coverage is version-sensitive. Record the evidence date and software version when available.

## 9. Data Scope

Include only information that helps a locksmith identify or prepare for a key-programming job.

Include:

- key and security data;
- programming compatibility;
- necessary accessories and access requirements;
- programming-relevant module locations;
- concise warnings.

Exclude unless directly relevant:

- general diagnostics;
- service schedules;
- unrelated wiring;
- alarm features that do not affect key programming;
- long manufacturer history;
- generic repair procedures.

## 10. Repository Structure

Model data follows this structure:

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

Manufacturer-level files may include:

```text
database/vehicles/<manufacturer>/
├── manifest.json
├── platforms.json
└── key_systems.json
```

Documentation uses the existing capitalised `Docs/` folder.

## 11. Change Control

Every material change must record:

- what changed;
- why it changed;
- the evidence used;
- the date;
- the affected records;
- whether JSON or app testing is required again.

Significant architecture decisions belong in `Docs/DESIGN_DECISIONS.md`.

User-facing database changes belong in `Docs/CHANGELOG.md`.

## 12. Git and Commit Standard

Commits should be small enough to review and should describe the actual change.

Recommended formats:

- `docs: add security-generation audit standard`
- `ford: split Transit Custom records by verified security generation`
- `ford: verify Fiesta keyed tool compatibility`
- `schema: simplify tool support fields`
- `data: generate verified Ford model JSON`

Do not label a commit as verified when it contains unresolved assumptions.

## 13. Definition of Manufacturer Complete

A manufacturer is complete only when:

- UK model inventory is complete;
- security-generation splits are locked;
- technical fields are audited;
- held fields are clearly marked and do not create unsafe guidance;
- JSON is generated and validated;
- manifests and versions are updated;
- the app downloads and displays the data correctly;
- Android/offline testing passes;
- project status and changelog are updated.

## 14. Current Priority

Ford is the reference manufacturer for this standard.

Before another brand begins, Ford must complete:

1. full security-generation split audit;
2. technical field verification;
3. Ford JSON generation;
4. app download and display testing;
5. final manufacturer sign-off.

Future manufacturers must follow the same sequence from the start.
