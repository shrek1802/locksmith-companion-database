# Project Status

## Current Vehicle
Ford Fiesta 2008–2012 (UK RHD, keyed ignition)

## Master Workbook
`Locksmith_Master_Research_Database_v1.xlsx`

The workbook is the single source of truth. Chat-only summaries are not approved unless entered into the workbook with evidence.

## Current Work
Full Ford model audit before generating JSON or moving to another manufacturer.

## Immediate Corrections Identified
- Ford Ka Mk2 (2008–2016) remains under Ford Ka, but uses Fiat 312 / Fiat CODE architecture rather than normal Ford PATS assumptions.
- Transit Connect Mk3 and Tourneo Connect Mk3 remain under Ford, but are Volkswagen Caddy / MQB-based partnership vehicles and require separate generation records.
- Ford Explorer EV and Ford Capri EV are Volkswagen MEB-based and must not inherit conventional Ford PATS assumptions.
- Transit Custom / Tourneo Custom Mk2 (2023+) must be separated from Mk1.
- Ranger 2023+ must be separated from the 2012–2022 generation.

## FDRS Rule
There is no single universal model year when every Ford changed to FDRS. Record FDRS only when verified for the exact model, generation, build range and immobiliser operation.

Allowed security-family values include:
- Traditional PATS
- PATS with FDRS service workflow
- FDRS-required
- Fiat CODE
- Volkswagen MQB
- Volkswagen MEB
- Other verified platform/security family

## Research Scope
Only information directly useful for UK auto-locksmith key identification and programming:
- Vehicle and ignition variant
- Underlying platform / security family where relevant
- Blade, transponder, frequency and key type
- Add key / all keys lost / erase / parameter reset
- OBD, EEPROM or bench route
- Security or online requirements
- Tool support by individual function
- Programming-relevant module locations
- Concise warnings and job notes
- Evidence sources

## Verification Rule
Approve a field when supported by:
- an official manufacturer source, or
- two independent professional sources that agree, or
- clear workshop evidence.

Hold fields where sources conflict, evidence is weak, or an error could create programming/module risk.

## JSON
Do not generate or update vehicle JSON until the Ford audit and the full Fiesta model family have been signed off in the workbook.

## Next Task
Finish the Ford Fiesta 2008–2012 keyed record in the simplified workbook, then audit each remaining Ford generation individually.

## Schema
Database Schema v1.0 (SIMPLIFIED AND LOCKED)

## Research Standard
Research Standards v1.0 (PRACTICAL UK KEY-PROGRAMMING STANDARD)
