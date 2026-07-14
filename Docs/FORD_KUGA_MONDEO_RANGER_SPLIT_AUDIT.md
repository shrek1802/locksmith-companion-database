# Ford Kuga, Mondeo and Ranger Security Split Audit

**Version:** 1.0  
**Status:** In progress  
**Last updated:** 2026-07-14  
**Scope:** UK-market badge records, security-generation boundaries only

## Purpose

This document records the provisional security-generation split plan for Ford Kuga, Mondeo and Ranger before technical key data is approved.

A facelift is not treated as a security split unless evidence shows a locksmith-relevant change.

## Kuga

### Confirmed vehicle generations

- First generation: 2008–2012.
- Second generation: 2013–2019, with a facelift during the generation.
- Third generation: 2020–present on Ford C2 architecture, with a later facelift still inside the same generation unless security evidence proves otherwise.

### Provisional record plan

| Proposed record | Status | Reason |
|---|---|---|
| Kuga 2008–2012 keyed | verification_required | First generation boundary is clear; exact security/key continuity still needs proof. |
| Kuga 2008–2012 passive start | verification_required | Verify whether UK passive-start fitment existed and whether it requires separate data. |
| Kuga 2013–2019 keyed | split_required | Second generation; keep facelift inside the range unless security evidence proves a change. |
| Kuga 2013–2019 passive start | split_required | Passive-start record required where fitted. |
| Kuga 2020–present keyed | split_required | Third generation/C2; verify keyed availability and operation-specific FDRS. |
| Kuga 2020–present passive start | split_required | Third generation/C2 smart-key record; verify facelift and FDRS impact. |

### Kuga audit note

The 2017 and 2024 styling updates do not create automatic security records. Exact transponder, BCM, tool support and FDRS data remain unapproved.

## Mondeo

### Confirmed vehicle generations

- First-generation/facelift family: 1993–2000, with the major 1996 facelift commonly badged as Mk II.
- Second-generation family: 2000–2007.
- Third European generation: 2007–2014, with a 2010 facelift.
- Fourth European/global generation: UK sales from 2014/2015 to production end in 2022.

### Provisional record plan

| Proposed record | Status | Reason |
|---|---|---|
| Mondeo 1996–2000 keyed | verification_required | Inventory starts in the transponder-relevant facelift era; verify exact PATS breakpoint. |
| Mondeo 2000–2007 keyed | verification_required | Separate generation; verify whether one keyed security system covers the full range. |
| Mondeo 2007–2014 keyed | split_required | New generation; 2010 facelift stays inside unless security evidence proves a change. |
| Mondeo 2007–2014 passive start | split_required | Verify UK passive-start fitment and exact introduction. |
| Mondeo 2014–2022 keyed | split_required | New global generation; verify keyed availability. |
| Mondeo 2014–2022 passive start | split_required | Separate smart-key record; verify online/FDRS by operation and build. |

### Mondeo audit note

The 2010 facelift is not an automatic security breakpoint. The delayed European launch of the final generation should be recorded using UK availability, not the earlier North American reveal date.

## Ranger

### Confirmed vehicle generations

- Mazda-derived international Ranger family before the Ford-designed T6 generation.
- T6/P375 generation introduced for Europe in 2012 and continuing through the 2015/2016 facelift to 2022.
- P703/current generation introduced in Europe from late 2022/2023.

### Provisional record plan

| Proposed record | Status | Reason |
|---|---|---|
| Ranger 1999–2006 keyed | shared_platform | Mazda B-Series-derived first international generation; verify security family. |
| Ranger 2006–2011 keyed | shared_platform | Mazda BT-50-related second international generation; separate from 1999–2006. |
| Ranger 2012–2022 keyed | split_required | Ford-designed T6/P375 generation. Do not split at the 2015/2016 facelift without security evidence. |
| Ranger 2012–2022 passive start | split_required | Separate record where passive start was fitted; exact UK introduction must be verified. |
| Ranger 2023–present keyed | split_required | New P703/current generation; verify keyed availability. |
| Ranger 2023–present passive start | split_required | New generation smart-key record; verify FDRS and tool support by operation. |

### Ranger audit note

The earlier 1999–2011 single inventory range is too broad. It contains at least two Mazda-derived generations and must be split before technical auditing.

## Evidence Quality

The vehicle-generation boundaries above are sufficient to correct broad inventory ranges. They are not sufficient to approve:

- transponder type;
- blade or emergency blade;
- frequency;
- Add Key or All Keys Lost support;
- tool compatibility;
- FDRS/online requirements;
- exact passive-start build ranges.

Those remain part of the technical audit.

## Required Master-File Changes

1. Update the master Ford inventory so Ranger 1999–2011 becomes 1999–2006 and 2006–2011.
2. Keep Kuga 2013–2019 as one generation across its facelift unless security evidence proves otherwise.
3. Keep Mondeo 2007–2014 as one generation across the 2010 facelift unless security evidence proves otherwise.
4. Keep Ranger 2012–2022 as one T6/P375 generation across the 2015/2016 facelift unless security evidence proves otherwise.
5. Continue to separate keyed and passive-start variants only where fitted and locksmith-relevant.
