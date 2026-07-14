# Ford Courier Security Split Audit

**Version:** 1.0  
**Status:** In progress  
**Last updated:** 2026-07-14  
**Scope:** UK-market Ford Courier, Transit Courier and Tourneo Courier badge records

## Purpose

This document records provisional security-generation boundaries for the Ford Courier family before technical key data is approved.

A facelift or powertrain change is not treated as a new locksmith record unless security architecture, key type, programming route or tool compatibility changes.

## Ford Courier 1991–2002

### Confirmed boundary

- The European Ford Courier van was Fiesta-based and ran through the 1990s to 2002.
- This badge must remain separate from the later Transit Courier/Tourneo Courier family.

### Provisional record plan

| Proposed record | Status | Reason |
|---|---|---|
| Courier 1991–1995 keyed | verification_required | Verify whether early vehicles were pre-transponder and whether the database should start later. |
| Courier 1995–2002 keyed | verification_required | Verify PATS/transponder introduction and whether one security generation covers the range. |

## Transit Courier and Tourneo Courier — First Generation

### Confirmed generation boundary

- First generation introduced for the 2014 model year.
- It was based on Ford's global B platform shared with Fiesta/B-Max.
- Transit Courier and Tourneo Courier are separate badge records but share the same underlying vehicle generation.
- Later styling updates remain within the first generation unless security evidence proves a change.

### Provisional record plan

| Proposed record | Status | Reason |
|---|---|---|
| Transit Courier 2014–2023 keyed | verification_required | First generation; verify whether one keyed security generation spans the full range. |
| Transit Courier 2014–2023 passive start | verification_required | Create only where UK fitment is confirmed. |
| Tourneo Courier 2014–2023 keyed | verification_required | Separate passenger badge; verify whether security data mirrors Transit Courier. |
| Tourneo Courier 2014–2023 passive start | verification_required | Create only where UK fitment is confirmed. |

## Transit Courier and Tourneo Courier — Second Generation

### Confirmed generation boundary

- Second generation introduced from 2023.
- It moved to a newer Ford platform related to the Puma rather than the first-generation Fiesta/B-Max platform.
- It is not Volkswagen-derived.
- Electric variants belong to this second generation, but EV versus ICE is only split where key/security workflow differs.

### Provisional record plan

| Proposed record | Status | Reason |
|---|---|---|
| Transit Courier 2023–present keyed | split_required | New generation; verify keyed availability and security architecture. |
| Transit Courier 2023–present passive start | split_required | Separate where fitted; verify FDRS/online requirements. |
| E-Transit Courier 2024–present passive start | split_required | Separate only if electric model uses different key/security workflow. |
| Tourneo Courier 2023–present keyed | split_required | New passenger generation; verify keyed availability. |
| Tourneo Courier 2023–present passive start | split_required | Verify smart-key and online requirements. |
| E-Tourneo Courier 2024–present passive start | split_required | Separate only if electric model differs in key/security workflow. |

## Evidence Quality

The first/second-generation boundary and the platform change are sufficient to correct inventory ranges. They do not approve:

- transponder type;
- blade profile;
- frequency;
- BCM/security generation;
- Add Key or All Keys Lost support;
- exact passive-start availability;
- FDRS or online requirement;
- tool compatibility.

## Master-File Actions

1. Keep Courier 1991–2002 separate from Transit/Tourneo Courier.
2. Keep Transit Courier and Tourneo Courier under their own badge names.
3. Use 2014–2023 for first-generation Transit/Tourneo Courier.
4. Use 2023–present for second-generation Transit/Tourneo Courier.
5. Do not label the second generation as Volkswagen-derived.
6. Add separate E-Transit/E-Tourneo Courier records only if technical audit proves different locksmith workflow.
