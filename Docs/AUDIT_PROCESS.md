# Vehicle Audit Process

**Version:** 1.0  
**Status:** Approved  
**Last updated:** 2026-07-14

## Purpose

This document defines the mandatory evidence-based audit process for every manufacturer and vehicle record.

## Audit Sequence

1. Build the complete UK badge-name inventory.
2. Confirm UK sale years and model identity.
3. Identify shared platforms and rebadged vehicles.
4. Audit security-generation splits.
5. Lock the model/year/ignition record list.
6. Verify technical fields individually.
7. Verify tool compatibility by operation.
8. Record evidence and unresolved conflicts.
9. Generate and validate JSON.
10. Test the data in the app.

## Security-Split Audit

Create a separate record where any of the following changes:

- immobiliser or security generation;
- keyed versus passive start;
- transponder family;
- BCM, IPC, KESSY, CAS, FEM, BDC, BSI, UCH or equivalent module;
- programming route;
- OBD, bench or EEPROM requirement;
- online, FDRS, SFD or SGW requirement;
- underlying platform manufacturer;
- confirmed VIN or build-date breakpoint.

Do not split for a cosmetic facelift unless the locksmith-relevant system changed.

## Technical Checklist

Verify each field separately:

- badge name;
- UK year range;
- ignition type;
- platform and security family;
- blade or emergency blade;
- transponder;
- UK frequency;
- battery where confirmed;
- Add Key;
- All Keys Lost;
- erase or reset functions;
- programming route;
- online and gateway requirements;
- required cable or adaptor;
- tool compatibility by function;
- UK RHD module location;
- warnings and concise job notes.

## Source Collection

For each field, record:

- source name;
- source type;
- URL or document reference;
- publication or software date where available;
- exact field supported;
- any limitations or market differences.

## Conflict Handling

When sources disagree:

1. Prefer the higher-ranked source in `Docs/EVIDENCE_HIERARCHY.md`.
2. Check whether the conflict is caused by market, ignition type, build date or trim.
3. Split the record if the difference is real and locksmith-relevant.
4. Use `verification_required` when the conflict cannot be resolved.
5. Never choose the most convenient answer merely to complete the record.

## Tool Compatibility Audit

Compatibility must be verified per operation:

- Add Key;
- All Keys Lost;
- erase keys;
- parameter reset or synchronisation;
- security-data read;
- EEPROM or bench operation;
- remote/key generation only.

Record tool model, software version and evidence date where available.

A key generator must not be marked as an immobiliser programmer unless it performs the programming function itself.

## Shared-Platform Rule

Keep the vehicle under the badge the locksmith sees. Record the true platform/security family inside the record.

Examples include Ford-badged vehicles using Fiat, Volkswagen, Mazda or Nissan security architecture.

## Sign-Off States

- `verified` — evidence meets the standard.
- `verification_required` — insufficient or conflicting evidence.
- `vin_or_build_dependent` — confirmed variation without a universal breakpoint.
- `unsupported` — confirmed unavailable.
- `not_applicable` — does not apply.
- `unknown` — no reliable evidence found.

## Audit Completion

A record is ready for JSON only when:

- its split is locked;
- all critical fields are verified or clearly held;
- evidence is recorded;
- tool support is operation-specific;
- no vague wording is presented as fact;
- the change log and project status can be updated accurately.
