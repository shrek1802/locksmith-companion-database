# Ford UK Model Inventory

This is the master Ford audit list for the UK auto-locksmith database.

## Search Rule

Vehicles are listed by the badge name a locksmith sees on the vehicle, followed by the year range. Underlying platform and security-family information belongs inside the record and does not replace the Ford badge name.

## Scope

The inventory begins with vehicles relevant to transponder-era key programming, broadly from the mid-1990s onward. Very rare official models may be lower priority but remain listed.

## Passenger Cars

- Escort — 1995–2000 car; van to 2002
- Scorpio — 1994–1998
- Probe — 1994–1997
- Ka — 1996–2008
- Ka — 2008–2016 — Fiat 312 / Fiat CODE exception
- Ka+ — 2016–2020
- StreetKa — 2003–2005
- Fiesta — 1995–2001
- Fiesta — 2002–2008
- Fiesta — 2008–2012
- Fiesta — 2013–2017
- Fiesta — 2017–2023
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
- Cougar — 1998–2002
- Galaxy — 1995–2000 — Volkswagen Sharan/VAG exception
- Galaxy — 2000–2006 — Volkswagen Sharan/VAG exception
- Galaxy — 2006–2015
- Galaxy — 2015–2023
- S-Max — 2006–2015
- S-Max — 2015–2023

## SUVs, Pick-ups and Performance Models

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
- Mustang — 2015–present
- Mustang Mach-E — 2021–present
- GT — 2005–2006 — very low priority
- Ranger — 1999–2011 — Mazda B-Series-derived exception
- Ranger — 2012–2022
- Ranger — 2023–present

## Vans and Tourneo Models

- Courier — 1991–2002
- Transit Courier — 2014–2023
- Transit Courier — 2023–present
- Tourneo Courier — 2014–2023
- Tourneo Courier — 2023–present
- Transit Connect — 2002–2013
- Transit Connect — 2013–2024
- Transit Connect — 2024–present — Volkswagen Caddy/MQB exception
- Tourneo Connect — 2002–2013
- Tourneo Connect — 2013–2022
- Tourneo Connect — 2022–present — Volkswagen Caddy/MQB exception
- Transit Custom — 2012–2023
- Transit Custom — 2023–present
- Tourneo Custom — 2012–2023
- Tourneo Custom — 2023–present
- Transit — 1994–2000
- Transit — 2000–2006
- Transit — 2006–2014
- Transit — 2014–2023
- Transit — 2024–present
- Tourneo — 1995–2006

## Shared-Platform Audit Rules

- Keep every vehicle under its Ford badge name.
- Record the underlying security platform inside the vehicle record.
- Do not apply Ford PATS defaults to Fiat-, Volkswagen-, Nissan- or Mazda-derived vehicles.
- Galaxy 1995–2006 requires VAG-specific immobiliser research.
- Ka 2008–2016 requires Fiat CODE/body-computer research.
- Transit Connect 2024+ and Tourneo Connect 2022+ require Volkswagen MQB research.
- Explorer EV and Capri EV require Volkswagen MEB/Ford workflow research.
- Ranger 1999–2011 requires Mazda-derived system verification.

## FDRS Rule

There is no universal Ford FDRS start year. FDRS must be recorded only after verification for the exact badge, generation, build range and immobiliser operation.

## Current Audit Order

1. Finish Fiesta 2008–2012 keyed ignition.
2. Complete all Fiesta year and ignition variants.
3. Audit the remaining Ford records by badge and year.
4. Correct all shared-platform exceptions.
5. Generate JSON only after the full Ford model family is signed off in the master workbook.
