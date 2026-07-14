# Ford Security Generation Split Audit

**Version:** 1.0  
**Status:** In progress  
**Last updated:** 2026-07-14  
**Scope:** UK-market Ford vehicles, badge-name search, key-programming relevance only

## Purpose

This file tracks the Ford record-splitting audit before technical fields or JSON are finalised.

A record is split only when a locksmith-relevant change affects key choice, security architecture, programming route, online/gateway access, required equipment or tool compatibility.

## Status Values

- `locked` — record boundary supported by evidence and ready for technical audit.
- `split_required` — separate records are definitely required, but exact breakpoint or variant list still needs confirmation.
- `verification_required` — current inventory range is not yet proven as one security generation.
- `shared_platform` — badge remains Ford; underlying security architecture comes from another manufacturer.
- `low_priority` — retained in inventory but audited after common UK vehicles.

## Locked Shared-Platform Rules

| Ford badge/model | Ford inventory range | Audit status | Underlying architecture | Required action |
|---|---:|---|---|---|
| Ka | 2008–2016 | shared_platform | Fiat 312 / Fiat CODE | Keep under Ford Ka; research Fiat-based security and procedures. |
| Galaxy | 1995–2006 | shared_platform | Volkswagen Sharan/SEAT Alhambra family | Keep under Ford Galaxy; split by verified VAG immobiliser generation. |
| Transit Connect | 2024–present | shared_platform | Volkswagen Caddy V / MQB | Keep under Ford Transit Connect; verify MQB key and online requirements. |
| Tourneo Connect | 2022–present | shared_platform | Volkswagen Caddy V / MQB | Keep under Ford Tourneo Connect; verify MQB key and online requirements. |
| Explorer EV | 2024–present | shared_platform | Volkswagen MEB | Keep under Ford Explorer; do not inherit conventional Ford PATS data. |
| Capri EV | 2024–present | shared_platform | Volkswagen MEB | Keep under Ford Capri; do not inherit conventional Ford PATS data. |
| Ranger | 1999–2011 | shared_platform | Mazda-derived | Keep under Ford Ranger; verify Mazda/Ford security generations. |
| Probe | 1994–1997 | shared_platform | Mazda-derived | Keep under Ford Probe; verify exact immobiliser architecture. |
| Maverick | 1993–1999 | shared_platform | Nissan Terrano II-derived | Keep under Ford Maverick; verify Nissan-derived security. |
| Maverick | 2001–2007 | shared_platform | Mazda Tribute/Ford Escape-derived | Separate from the earlier Maverick generation. |

## High-Priority Passenger Models

| Badge/model | Inventory range | Split audit status | Current decision |
|---|---:|---|---|
| Fiesta | 1995–2001 | verification_required | Verify early PATS/transponder breakpoints. |
| Fiesta | 2002–2008 | verification_required | Verify whether one keyed security generation covers the full UK range. |
| Fiesta | 2008–2012 | verification_required | Keyed record expected; confirm any passive-start UK variant before locking. |
| Fiesta | 2013–2017 | split_required | Separate keyed and passive-start records where fitted. Exact technical data remains unapproved. |
| Fiesta | 2017–2023 | split_required | Separate keyed and passive-start records; check later build/security changes before locking. |
| Focus | 1998–2004 | verification_required | Verify early/late PATS, blade and transponder breakpoints. |
| Focus | 2004–2011 | split_required | Verify keyed/passive availability and whether a security breakpoint is required. |
| Focus | 2011–2018 | split_required | Keyed and passive-start records required; check facelift/build changes. |
| Focus | 2018–2025 | split_required | Keyed and passive-start records required; verify 2022 facelift/security effects and FDRS by operation. |
| Mondeo | 1996–2000 | verification_required | Verify early transponder/PATS generation. |
| Mondeo | 2000–2007 | verification_required | Confirm security generation and any passive-start introduction. |
| Mondeo | 2007–2014 | split_required | Verify keyed/passive records and any facelift security change. |
| Mondeo | 2014–2022 | split_required | Separate ignition variants; verify online/FDRS by build and operation. |
| Kuga | 2008–2012 | verification_required | Confirm keyed/passive variants and record boundaries. |
| Kuga | 2013–2019 | split_required | Separate keyed/passive records; verify facelift/build changes. |
| Kuga | 2020–present | split_required | Current C2 generation; verify hybrid/PHEV/security differences and FDRS by operation. |
| Puma | 1997–2002 | verification_required | Verify one Ford PATS generation. |
| Puma | 2019–present | split_required | Separate keyed/passive where applicable; verify facelift and current security access. |

## MPV and SUV Models

| Badge/model | Inventory range | Split audit status | Current decision |
|---|---:|---|---|
| Focus C-Max | 2003–2007 | verification_required | Keep badge name Focus C-Max; verify security generation. |
| C-Max | 2007–2010 | verification_required | Verify keyed/passive applicability. |
| C-Max | 2010–2019 | split_required | Separate keyed/passive records where fitted; check facelift/build security changes. |
| Grand C-Max | 2010–2019 | split_required | Separate keyed/passive records where fitted. |
| B-Max | 2012–2017 | split_required | Verify keyed/passive variants and shared Fiesta architecture. |
| EcoSport | 2014–2023 | split_required | Verify keyed/passive variants and facelift/security breakpoint. |
| Edge | 2016–2019 | verification_required | Passive-start likely dominant; verify whether any UK keyed record is needed. |
| Galaxy | 2006–2015 | split_required | Ford-developed generation; verify keyed/passive records. |
| Galaxy | 2015–2023 | split_required | Verify passive/keyed variants and online/FDRS requirements. |
| S-Max | 2006–2015 | split_required | Verify keyed/passive records. |
| S-Max | 2015–2023 | split_required | Verify later architecture, passive/keyed variants and online requirements. |
| Explorer | 1997–2001 | low_priority | Verify UK RHD security architecture. |
| Explorer PHEV | 2020–2023 | verification_required | Verify smart-key architecture and online requirements. |
| Mustang | 2015–present | split_required | Separate S550 and S650 security generations; verify UK smart-key workflow. |
| Mustang Mach-E | 2021–present | verification_required | Verify passive key, phone-as-key and online/FDRS implications. |

## Commercial Vehicles

| Badge/model | Inventory range | Split audit status | Current decision |
|---|---:|---|---|
| Transit | 1994–2000 | verification_required | Verify transponder introduction and Mk5 PATS split. |
| Transit | 2000–2006 | verification_required | Verify Mk6 security generation. |
| Transit | 2006–2014 | verification_required | Verify whether one Mk7 keyed record is sufficient. |
| Transit | 2014–2023 | split_required | Audit exact security/ignition/build splits; do not use one broad record without evidence. |
| Transit | 2024–present | split_required | Current range needs separate security/FDRS audit, including E-Transit where relevant. |
| Transit Custom | 2012–2023 | split_required | Broad inventory range is not locked. Verify exact security breakpoints and ignition variants before technical audit. |
| Transit Custom | 2023–present | split_required | New generation; verify keyed/passive/electric variants and FDRS. |
| Tourneo Custom | 2012–2023 | split_required | Verify ignition variants and whether splits mirror Transit Custom. |
| Tourneo Custom | 2023–present | split_required | New generation; verify smart-key and online security. |
| Transit Connect | 2002–2013 | verification_required | Verify Mk1 security generation and key changes. |
| Transit Connect | 2013–2024 | split_required | Verify ignition variants and exact security breakpoints. |
| Tourneo Connect | 2002–2013 | verification_required | Verify Mk1 passenger derivative. |
| Tourneo Connect | 2013–2022 | split_required | Verify keyed/passive variants and generation end date. |
| Transit Courier | 2014–2023 | verification_required | Verify keyed/passive and facelift security changes. |
| Transit Courier | 2023–present | split_required | New generation; verify ICE/EV and online requirements. |
| Tourneo Courier | 2014–2023 | verification_required | Verify whether record boundaries mirror Transit Courier. |
| Tourneo Courier | 2023–present | split_required | New generation; verify ICE/EV and smart-key variants. |
| Ranger | 2012–2022 | split_required | Separate keyed/passive records and verify facelift/security changes. |
| Ranger | 2023–present | split_required | T6.2/current generation; verify FDRS and exact tool support by operation. |

## Remaining and Low-Priority Models

Escort, Scorpio, StreetKa, Ka+, Fusion, Cougar, Courier, Tourneo and Ford GT remain in the inventory. Their split audits are required before Ford can be signed off, but they follow the high-volume UK models.

## FDRS Rule

There is no universal Ford FDRS start year.

FDRS status must be verified for:

- exact badge/model;
- exact security generation;
- build range where relevant;
- exact operation, such as Add Key, All Keys Lost or module replacement.

Allowed released values are:

- `not_required`
- `required`
- `vin_or_build_dependent`
- `verification_required`

## Next Audit Actions

1. Lock the Fiesta record splits using current evidence.
2. Lock the Focus record splits.
3. Audit Transit, Transit Custom and Transit Connect breakpoints.
4. Audit Ranger, Kuga and Mondeo.
5. Finish shared-platform records.
6. Complete all remaining/low-priority Ford models.
7. Only then begin the field-by-field technical audit and Ford JSON generation.
