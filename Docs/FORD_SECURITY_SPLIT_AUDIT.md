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
| Fiesta | 2008–2017 | split_required | One B299/B409 generation across pre-facelift and facelift. Do not split at 2013 merely for facelift. Separate keyed and passive-start variants where fitted; verify whether technical/security breakpoints exist within the generation. |
| Fiesta | 2017–2023 | split_required | New seventh-generation model. Separate keyed and passive-start variants; verify whether the 2022 facelift changed locksmith-relevant security before adding another split. |
| Focus | 1998–2004 | verification_required | One first-generation platform with a 2001 facelift. Do not split at facelift unless PATS/key evidence proves a change. |
| Focus | 2004–2011 | split_required | Keep one keyed generation unless technical evidence proves otherwise. Add a separate passive-start record from the 2008 facelift because Ford Power Button was introduced then. |
| Focus | 2011–2018 | split_required | New third generation. Separate keyed and passive-start records; the 2014/2015 facelift is not automatically a security split. |
| Focus | 2018–2025 | split_required | New C2 generation. Separate keyed and passive-start records; verify whether the 2022 refresh changed locksmith-relevant security and FDRS by operation. |
| Mondeo | 1996–2000 | verification_required | Verify early transponder/PATS generation. |
| Mondeo | 2000–2007 | verification_required | Confirm security generation and any passive-start introduction. |
| Mondeo | 2007–2014 | split_required | Verify keyed/passive records and any facelift security change. |
| Mondeo | 2014–2022 | split_required | Separate ignition variants; verify online/FDRS by build and operation. |
| Kuga | 2008–2012 | verification_required | Confirm keyed/passive variants and record boundaries. |
| Kuga | 2013–2019 | split_required | Separate keyed/passive records; verify facelift/build changes. |
| Kuga | 2020–present | split_required | Current C2 generation; verify hybrid/PHEV/security differences and FDRS by operation. |
| Puma | 1997–2002 | verification_required | Verify one Ford PATS generation. |
| Puma | 2019–present | split_required | Separate keyed/passive where applicable; verify facelift and current security access. |

## Fiesta Split Findings — Pass 1

### Confirmed generation boundaries

- The sixth-generation Fiesta was produced from 2008 and continued through its facelifted form to 2017.
- The seventh-generation Fiesta is a separate vehicle generation produced from 2017 to July 2023.
- The 2013 change is therefore a facelift boundary, not automatically a security-generation boundary.
- The seventh-generation car received a facelift for 2022, but this does not yet justify a separate locksmith record without evidence of a security/programming change.

### Confirmed ignition-variant requirement

- Keyless entry with a Ford Power starter button existed within the 2008–2017 generation.
- Keyed and passive-start variants must therefore be audited separately across the applicable UK ranges.

### Provisional Fiesta record plan

| Proposed record | Status | Reason |
|---|---|---|
| Fiesta 1995–2001 keyed | verification_required | Early PATS/transponder breakpoint still needs evidence. |
| Fiesta 2002–2008 keyed | verification_required | Generation boundary is clear; exact security continuity still needs proof. |
| Fiesta 2008–2017 keyed | split_required | Same vehicle generation across facelift; technical/security breakpoint must be checked before lock. |
| Fiesta 2008–2017 passive start | split_required | Passive-start option existed; exact UK availability and technical breakpoint must be checked. |
| Fiesta 2017–2023 keyed | split_required | New generation; verify whether 2022 facelift changes security. |
| Fiesta 2017–2023 passive start | split_required | New generation; verify whether 2022 facelift changes security. |

### Evidence quality note

The generation and feature-existence findings are sufficient to remove the unsupported 2008–2012/2013–2017 facelift split from the master plan. They are not yet sufficient to approve transponder, tool support, FDRS or exact passive-start build ranges.

## Focus Split Findings — Pass 1

### Confirmed generation boundaries

- First generation: 1998–2004/2005 in Europe, with a 2001 facelift.
- Second European generation: late 2004–2011, with the UK facelift on sale from February 2008.
- Third generation: 2011–2018 in Europe.
- Fourth generation: 2018–2025 on Ford C2 architecture, with a 2022 refresh.

### Confirmed ignition-variant finding

- The second-generation Focus offered KeyFree technology.
- The 2008 UK facelift specifically introduced a Ford Power Button.
- A passive-start record is therefore required for the applicable 2008–2011 vehicles, rather than treating all 2004–2011 cars as one keyed record.

### Provisional Focus record plan

| Proposed record | Status | Reason |
|---|---|---|
| Focus 1998–2004 keyed | verification_required | Generation boundary is clear; verify whether the 2001 facelift changed PATS/key technology. |
| Focus 2004–2011 keyed | split_required | Keyed variant spans the second generation; confirm no security breakpoint at the 2008 facelift. |
| Focus 2008–2011 passive start | split_required | Ford Power Button introduced with the 2008 UK facelift. Exact trim/build availability still needs confirmation. |
| Focus 2011–2018 keyed | split_required | New generation; verify whether the facelift changes security. |
| Focus 2011–2018 passive start | split_required | Passive-start option requires separate key/programming data. |
| Focus 2018–2025 keyed | split_required | C2 generation; verify 2022 refresh and FDRS impact. |
| Focus 2018–2025 passive start | split_required | C2 passive-start record; verify 2022 refresh and FDRS impact. |

### Focus evidence quality note

The generation boundaries and the need for a 2008–2011 passive-start record are supported. Exact PATS generations, transponders, facelift breakpoints and tool/FDRS coverage remain unapproved until the technical audit.

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
| Transit | 1994–2000 | verification_required | Mk5 generation; verify transponder introduction and any PATS breakpoint. |
| Transit | 2000–2006 | verification_required | Mk6/all-new 2000 generation; verify one security generation across pre-facelift production. |
| Transit | 2006–2014 | split_required | 2006 facelift introduced CAN-bus electronics. Treat as a separate security-era record from 2000–2006; verify whether later changes require another split. |
| Transit | 2014–present | split_required | All-new large Transit generation. Do not split at 2024 merely because of model-year updates; verify exact FDRS/security and E-Transit breakpoints by operation. |
| Transit Custom | 2012–2023 | split_required | First generation. Do not invent 2016/2017/2020 security splits without technical evidence. Separate keyed/passive variants where fitted and verify facelift effects. |
| Transit Custom | 2023–present | split_required | Second generation produced from 2023. Separate diesel/PHEV/electric only where security or key workflow differs; verify FDRS. |
| Tourneo Custom | 2012–2023 | split_required | First generation passenger derivative; verify whether ignition/security splits mirror Transit Custom. |
| Tourneo Custom | 2023–present | split_required | Second generation passenger derivative; verify smart-key and online security. |
| Transit Connect | 2002–2013 | verification_required | First generation Ford C170-derived. Verify security and key changes. |
| Transit Connect | 2013–2024 | split_required | Second Ford-developed generation. Verify keyed/passive variants and exact security breakpoints. |
| Transit Connect | 2024–present | shared_platform | Volkswagen Caddy V/MQB-based generation. Keep under Ford badge and use verified VAG architecture. |
| Tourneo Connect | 2002–2013 | verification_required | First generation passenger derivative. |
| Tourneo Connect | 2013–2022 | split_required | Second Ford-developed generation; verify keyed/passive variants. |
| Tourneo Connect | 2022–present | shared_platform | Volkswagen Caddy V/MQB-based generation. Keep under Ford badge and use verified VAG architecture. |
| Transit Courier | 2014–2023 | verification_required | Verify keyed/passive and facelift security changes. |
| Transit Courier | 2023–present | split_required | New generation; verify ICE/EV and online requirements. |
| Tourneo Courier | 2014–2023 | verification_required | Verify whether record boundaries mirror Transit Courier. |
| Tourneo Courier | 2023–present | split_required | New generation; verify ICE/EV and smart-key variants. |
| Ranger | 2012–2022 | split_required | Separate keyed/passive records and verify facelift/security changes. |
| Ranger | 2023–present | split_required | T6.2/current generation; verify FDRS and exact tool support by operation. |

## Transit Family Split Findings — Pass 1

### Confirmed generation boundaries

- Full-size Transit: 2000 introduced an all-new generation.
- The July 2006 facelift introduced CAN-bus electronics, making 2000–2006 and 2006–2014 separate locksmith-relevant audit eras even before key data is approved.
- The large Transit introduced for 2014 is a separate generation. A blanket 2024 split is not justified until a security/programming change is proven.
- Transit Custom first generation runs from 2012 to 2023.
- Transit Custom second generation was unveiled in 2022 and entered production in 2023.
- Tourneo Custom follows the same first/second-generation boundary but requires its own badge records.
- Transit Connect 2024+ and Tourneo Connect 2022+ are separate Volkswagen Caddy/MQB-derived generations.

### Corrected provisional record plan

| Proposed record | Status | Reason |
|---|---|---|
| Transit 1994–2000 | verification_required | Verify transponder introduction and Mk5 PATS. |
| Transit 2000–2006 | verification_required | All-new generation before CAN-bus facelift. |
| Transit 2006–2014 | split_required | CAN-bus electronics introduced with 2006 facelift. |
| Transit 2014–present | split_required | One all-new generation; split only on proven security/FDRS or powertrain-key workflow changes. |
| Transit Custom 2012–2023 keyed | split_required | First generation; verify facelift/security continuity. |
| Transit Custom 2012–2023 passive start | split_required | Separate only where passive start was fitted. |
| Transit Custom 2023–present | split_required | Second generation; verify keyed/passive and online/FDRS differences. |
| Tourneo Custom 2012–2023 | split_required | Passenger badge; verify whether same security splits apply. |
| Tourneo Custom 2023–present | split_required | Second generation passenger badge. |
| Transit Connect 2002–2013 | verification_required | First Ford-developed generation. |
| Transit Connect 2013–2024 | split_required | Second Ford-developed generation; verify ignition variants. |
| Transit Connect 2024–present | shared_platform | Volkswagen MQB-derived. |
| Tourneo Connect 2002–2013 | verification_required | First passenger generation. |
| Tourneo Connect 2013–2022 | split_required | Second Ford-developed passenger generation. |
| Tourneo Connect 2022–present | shared_platform | Volkswagen MQB-derived. |

### Transit evidence quality note

The generation boundaries and the 2006 CAN-bus breakpoint are supported. Exact transponder families, passive-start availability, FDRS requirements, tool coverage and operation-specific breakpoints remain unapproved until the technical audit.

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

1. Verify the technical/security breakpoint within Fiesta 2008–2017 and exact UK passive-start availability.
2. Verify whether the 2022 Fiesta facelift changed locksmith-relevant security.
3. Verify Focus PATS/key changes at the 2001, 2008, 2014/2015 and 2022 facelifts.
4. Verify Transit passive-start availability and operation-specific FDRS breakpoints.
5. Audit Ranger, Kuga and Mondeo.
6. Finish shared-platform records.
7. Complete all remaining/low-priority Ford models.
8. Only then begin the field-by-field technical audit and Ford JSON generation.
