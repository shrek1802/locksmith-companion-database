# Ford UK Model Inventory

**Version:** 1.1  
**Status:** Security-split audit in progress  
**Last updated:** 2026-07-14

This is the master Ford audit list for the UK auto-locksmith database.

## Search Rule

Vehicles are listed by the badge name a locksmith sees on the vehicle, followed by the UK year range. Underlying platform and security-family information belongs inside the record and does not replace the Ford badge name.

## Scope

The inventory begins with vehicles relevant to transponder-era key programming, broadly from the mid-1990s onward. Rare official models remain listed but may be lower priority.

A generation range below is an inventory boundary, not automatic proof that one technical security record covers the whole range. Keyed/passive, build-date and security-generation splits are locked separately in the Ford split-audit documents.

## Passenger Cars

- Escort car — 1995–2000
- Escort Van — 1995–2002
- Scorpio — 1994–1998
- Probe — 1994–1997 — Mazda-derived exception
- Cougar — 1998–2002
- Ka — 1996–2008 — Ford-derived first generation
- StreetKa — 2003–2005
- Ka — 2008–2016 — Fiat 312 / Fiat CODE exception
- Ka+ — 2016–2020
- Fiesta — 1995–2001
- Fiesta — 2002–2008
- Fiesta — 2008–2017 — one generation across 2013 facelift
- Fiesta — 2017–2023 — one generation across 2022 facelift unless security evidence proves otherwise
- Fusion — 2002–2012
- Puma — 1997–2002
- Puma — 2019–present
- Focus — 1998–2004
- Focus — 2004–2011
- Focus — 2011–2018
- Focus — 2018–2025
- Focus C-Max — 2003–2007
- C-Max — 2007–2010
- C-Max — 2010–2019
- Grand C-Max — 2010–2019
- B-Max — 2012–2017
- Mondeo — 1996–2000
- Mondeo — 2000–2007
- Mondeo — 2007–2014
- Mondeo — 2014–2022
- Galaxy — 1995–2000 — Volkswagen Sharan/VAG exception
- Galaxy — 2000–2006 — Volkswagen Sharan/VAG exception
- Galaxy — 2006–2015
- Galaxy — 2015–2023
- S-Max — 2006–2015
- S-Max — 2015–2023

## SUVs, Pick-ups, Performance and EV Models

- Maverick — 1993–1999 — Nissan Terrano II-derived exception
- Maverick — 2001–2007 — Mazda Tribute/Ford Escape-derived exception
- Kuga — 2008–2012
- Kuga — 2013–2019
- Kuga — 2020–present
- EcoSport — 2014–2023
- Edge — 2016–2019
- Explorer — 1997–2001
- Explorer — 2020–2023 PHEV
- Explorer — 2024–present EV — Volkswagen MEB exception
- Capri — 2024–present EV — Volkswagen MEB exception
- Mustang — 2015–2023 — S550
- Mustang — 2024–present — S650
- Mustang Mach-E — 2021–present — Ford GE1 EV
- Ford GT — 2005–2006 — very low priority
- Ford GT — 2017–2022 — very low priority
- Ranger — 1999–2006 — Mazda B-Series-derived exception
- Ranger — 2006–2011 — Mazda BT-50-related exception
- Ranger — 2012–2022 — Ford T6/P375
- Ranger — 2023–present — current/P703 generation

## Vans and Tourneo Models

- Courier — 1991–2002 — Fiesta-based legacy van
- Transit Courier — 2014–2023 — first generation
- Transit Courier — 2023–present — second generation
- Tourneo Courier — 2014–2023 — first generation
- Tourneo Courier — 2023–present — second generation
- Transit Connect — 2002–2013 — first Ford-developed generation
- Transit Connect — 2013–2024 — second Ford-developed generation
- Transit Connect — 2024–present — Volkswagen Caddy/MQB exception
- Tourneo Connect — 2002–2013
- Tourneo Connect — 2013–2022
- Tourneo Connect — 2022–present — Volkswagen Caddy/MQB exception
- Transit Custom — 2012–2023 — first generation
- Transit Custom — 2023–present — second generation
- Tourneo Custom — 2012–2023 — first generation
- Tourneo Custom — 2023–present — second generation
- Transit — 1994–2000
- Transit — 2000–2006
- Transit — 2006–2014 — separate CAN-bus era from 2000–2006
- Transit — 2014–present — split further only when security/FDRS evidence proves it
- Tourneo — 1995–2006

## Shared-Platform Audit Rules

- Keep every vehicle under its Ford badge name.
- Record the underlying security platform inside the vehicle record.
- Do not apply Ford PATS defaults to Fiat-, Volkswagen-, Nissan- or Mazda-derived vehicles.
- Galaxy 1995–2006 requires VAG-specific immobiliser research.
- Ka 2008–2016 requires Fiat CODE/body-computer research.
- Transit Connect 2024+ and Tourneo Connect 2022+ require Volkswagen MQB research.
- Explorer EV and Capri EV require Volkswagen MEB/Ford workflow research.
- Ranger 1999–2011 requires two separate Mazda-derived generation audits.
- Probe requires Mazda-derived security verification.
- Maverick requires separate Nissan-derived and Mazda/Ford-derived research.

## Ignition Variant Rule

Where fitted, keyed and passive-start variants are separate technical records. They may share the same model-generation year range but must not share unverified key, transponder or programming data.

## Facelift Rule

Do not split records for a facelift alone. Split only where evidence proves a locksmith-relevant change to security architecture, key type, programming route, required equipment, online access or tool compatibility.

## FDRS Rule

There is no universal Ford FDRS start year. FDRS must be recorded only after verification for the exact badge, generation, build range and immobiliser operation.

## Current Audit Order

1. Complete and lock all Ford model/security split boundaries.
2. Verify keyed and passive-start availability for each range.
3. Complete the field-by-field technical audit.
4. Correct all shared-platform security profiles.
5. Generate JSON only after the full Ford family is signed off.
6. Validate the Ford package in the Android app and offline updater.

## Related Audit Files

- `Docs/FORD_SECURITY_SPLIT_AUDIT.md`
- `Docs/FORD_KUGA_MONDEO_RANGER_SPLIT_AUDIT.md`
- `Docs/FORD_MPV_SUV_SPLIT_AUDIT.md`
- `Docs/FORD_COURIER_SPLIT_AUDIT.md`
- `Docs/FORD_PERFORMANCE_EV_SPLIT_AUDIT.md`
- `Docs/FORD_LEGACY_PASSENGER_SPLIT_AUDIT.md`
