# Ford Performance and EV Security Split Audit

**Version:** 1.0  
**Status:** In progress  
**Last updated:** 2026-07-14  
**Scope:** UK-market Mustang, Mustang Mach-E, Explorer EV, Capri EV and Ford GT badge records

## Purpose

This document records provisional security-generation boundaries for Ford performance and electric models before technical key and tool data are approved.

A powertrain or trim change is not treated as a new locksmith record unless it changes key type, security architecture, programming route, online access or tool compatibility.

## Mustang

### Confirmed generation boundaries

- S550 generation: UK-market right-hand-drive Mustang from 2015 to 2023.
- S650 generation: UK-market Mustang from 2024 onward.
- These generations require separate records regardless of visual similarity because the electrical/security architecture changed with the new generation.

### Provisional record plan

| Proposed record | Status | Reason |
|---|---|---|
| Mustang 2015–2023 passive start | split_required | S550 UK generation; verify exact key/security and FDRS requirements. |
| Mustang 2015–2023 keyed | verification_required | Create only if UK evidence confirms a true keyed-ignition variant. |
| Mustang 2024–present passive start | split_required | S650 generation; verify online/FDRS and tool support by operation. |
| Mustang 2024–present keyed | verification_required | Create only if UK evidence confirms fitment. |

## Mustang Mach-E

### Confirmed boundary

- Mustang Mach-E is a separate Ford GE1 battery-electric platform introduced for the 2021 model year.
- It must not share records with the combustion Mustang.
- Phone-as-key and digital-key features do not remove the need for a conventional passive-key record.

### Provisional record plan

| Proposed record | Status | Reason |
|---|---|---|
| Mustang Mach-E 2021–present passive start | split_required | Dedicated GE1 EV architecture; verify passive-key programming, phone-as-key interaction and FDRS. |

## Explorer EV

### Confirmed boundary

- Explorer EV production began in 2024 for Europe.
- It uses Volkswagen Group MEB architecture and is unrelated to the earlier large Ford Explorer/PHEV security platform.
- It remains searchable under the Ford Explorer badge.

### Provisional record plan

| Proposed record | Status | Reason |
|---|---|---|
| Explorer EV 2024–present passive start | shared_platform | Volkswagen MEB-derived; verify Ford/VAG key workflow, online access and tool support. |

## Capri EV

### Confirmed boundary

- Capri EV was introduced in 2024.
- It uses Volkswagen Group MEB architecture and is closely related to the Explorer EV.
- It must remain under the Ford Capri badge and must not inherit the classic Capri or Ford PATS records.

### Provisional record plan

| Proposed record | Status | Reason |
|---|---|---|
| Capri EV 2024–present passive start | shared_platform | Volkswagen MEB-derived; verify whether key/security workflow exactly matches Explorer EV before sharing technical data. |

## Explorer PHEV

### Provisional boundary

- Explorer PHEV 2020–2023 remains a separate conventional Ford record from Explorer EV.

| Proposed record | Status | Reason |
|---|---|---|
| Explorer PHEV 2020–2023 passive start | verification_required | Conventional Ford architecture; verify key/security and online requirements. |

## Ford GT

### Confirmed low-volume boundaries

- Ford GT 2005–2006 is the first modern GT generation in the current inventory.
- The later 2017–2022 Ford GT is a separate generation and should be added to the inventory despite very low UK volume.

### Provisional record plan

| Proposed record | Status | Reason |
|---|---|---|
| Ford GT 2005–2006 keyed/passive | low_priority | Verify exact ignition and transponder system. |
| Ford GT 2017–2022 passive start | low_priority | Separate generation; verify key/security and online requirements. |

## Evidence Quality

The platform and generation boundaries above are suitable for inventory correction. They do not approve:

- blade or emergency blade;
- transponder;
- frequency;
- Add Key/AKL support;
- phone-as-key enrolment procedure;
- tool compatibility;
- exact FDRS or online requirements.

## Master-File Actions

1. Split Mustang into 2015–2023 S550 and 2024–present S650.
2. Keep Mustang Mach-E as a separate GE1 EV model.
3. Keep Explorer PHEV separate from Explorer EV.
4. Mark Explorer EV and Capri EV as Volkswagen MEB-derived shared-platform records.
5. Add Ford GT 2017–2022 as a missing low-priority inventory generation.
6. Create keyed records only where UK-market evidence confirms keyed ignition.
