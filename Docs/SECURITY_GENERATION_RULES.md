# Security Generation Rules

**Version:** 1.0  
**Status:** Approved  
**Last updated:** 2026-07-14

## Purpose

These rules decide when one badge/model/year range must be divided into separate locksmith records.

## Create a New Record When

A separate record is mandatory when any of the following changes and could alter key choice, programming route or tool compatibility:

- keyed ignition changes to passive start;
- blade or emergency-blade family changes;
- transponder family or cryptographic technology changes;
- immobiliser generation changes;
- BCM, IPC, KESSY, CAS, FEM, BDC, BSI, UCH or smart-box generation changes;
- programming controller changes;
- Add Key or All Keys Lost method changes;
- OBD changes to EEPROM, bench or module removal;
- online access becomes mandatory;
- FDRS, SGW, SFD or equivalent gateway requirement changes;
- required cable, adaptor or bypass changes;
- underlying platform/security manufacturer changes;
- a verified VIN or build-date breakpoint changes the workflow.

## Do Not Split Solely Because Of

- cosmetic facelift;
- engine size;
- body style;
- trim level;
- marketing model-year change;
- remote button count;
- battery type;
- optional equipment that does not alter immobiliser programming.

Split for these only when evidence shows a real key-programming difference.

## Badge-Name Rule

The app always keeps the badge name the locksmith sees.

Examples:

- Ford Ka stays under Ford even when using Fiat CODE.
- Ford Galaxy stays under Ford even when using Volkswagen architecture.
- Ford Transit Connect stays under Ford when using Volkswagen MQB.

The underlying platform is stored inside the record.

## Keyed/Passive Rule

Keyed and passive-start variants must be separate records when they use different keys, transponders, modules or programming operations.

They may share a year range but must have clear ignition labels.

## Year-Break Rule

Use an exact year, build date or VIN break only when supported by evidence.

If a change is known but the breakpoint is not confirmed, use:

`vin_or_build_dependent`

Do not invent a clean calendar-year split.

## Security-Profile Rule

A new security profile is justified only by a reusable architectural change. A vehicle-specific trim difference normally creates a new vehicle record but not a new master security profile.

## Split Review Checklist

Before locking a split, confirm:

- UK-market applicability;
- the badge name;
- ignition variant;
- security controller;
- transponder/key technology;
- programming route;
- online/gateway requirements;
- tool support impact;
- evidence supporting the breakpoint.

## Approval

A proposed split becomes locked only after:

1. evidence is recorded;
2. conflicting sources are resolved or clearly held;
3. the manufacturer inventory is updated;
4. the reason is recorded in `Docs/CHANGELOG.md` or `Docs/DESIGN_DECISIONS.md`;
5. existing JSON is regenerated if already released.
