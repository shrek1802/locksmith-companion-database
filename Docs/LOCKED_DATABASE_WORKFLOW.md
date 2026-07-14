# Locked Database Workflow

Status: **ACTIVE AND LOCKED**

Effective date: 2026-07-14

This document defines the only approved workflow for building the Locksmith Companion database. Do not redesign the database, add more reference layers, or return to structure-first placeholder generation unless a proven technical blocker requires it.

## Primary objective

Every completed vehicle record must help a UK auto locksmith answer a customer enquiry faster than searching the web.

The first usable release is data-first. Photos are optional and may be added later.

## Four shared reference databases only

Vehicle records may reference only these shared databases for the first usable release:

1. Blade profiles
2. Transponders
3. Remote frequencies
4. Tools

Do not create additional shared databases for body style, fuel, gearbox, platform, manufacturer, key type, button count, battery, immobiliser name, or similar fields. Store those details directly in the vehicle record.

Existing extra reference files may remain for compatibility, but they are not to drive or delay current vehicle completion.

## Locksmith Card workflow

Research and complete one Locksmith Card for each exact UK model, generation, year range, and ignition type before exporting it into vehicle JSON.

### Vehicle identification

- Make
- Model
- Generation or Mk designation
- UK build/sale years
- Keyed ignition or passive/proximity
- Relevant facelift or security breakpoint

### Key and stock information

- Blade profile and blade ID
- Emergency blade where applicable
- Transponder/chip and transponder ID
- Remote frequency and frequency ID
- Key type
- Number of buttons
- Battery type
- OEM/Ford part numbers
- Useful aftermarket or supplier part references
- Xhorse/KEYDIY/universal-key option where supported

### Programming information

- Add Key supported
- All Keys Lost supported
- OBD, bench, EEPROM, module removal, or server route
- Online/FDRS requirement
- Immobiliser/BCM/KVM/module family
- Required cable, adaptor, bypass, or gateway access
- Important warnings and known failure points

### Tool compatibility

Map exact tool IDs from the existing tool database. At minimum, check the tools already relevant to the project, including:

- Autel IM508S / XP400 Pro
- Xhorse Key Tool Plus / Key Tool family
- KEYDIY KD-X4 / KD tools
- OBDSTAR
- Lonsdor
- Xtool

Do not guess support. Record operation-level support where possible: Add Key, AKL, PIN/security read, EEPROM, remote generation, and blade/key generation.

## Research rule

Use all relevant trusted sources in `database/reference/reference_sources.json` before leaving a core field unresolved.

Core fields are:

- Blade
- Transponder
- Frequency
- Key type
- OEM key part number
- Add Key route
- AKL route
- Tool compatibility

A field may be marked unresolved only when:

1. All relevant trusted sources have been checked; and
2. The result is genuinely VIN/build/market dependent, conflicting, subscription-only, or unavailable.

Do not mark a field unresolved simply because the first two sources did not provide it.

## Verification standard

- Prefer exact UK model/year/ignition matches.
- Use at least two independent professional sources where practical.
- One strong manufacturer or official tool source may approve an operation-specific claim when it is explicit.
- Google search and supplier results may be used to discover part numbers and applications, but important claims must be cross-checked.
- Never inherit US-only data into UK records.
- Never merge keyed and passive variants when their key or programming details differ.
- Split year ranges when blade, chip, security family, programming method, or required tool changes.

## Export rule

Only export a Locksmith Card into the live vehicle JSON when the core job information is useful and internally consistent.

A usable first-pass record should contain:

- Blade
- Transponder
- Frequency
- Key type
- OEM/stock references where available
- Add Key
- AKL
- Programming route
- Tool compatibility
- Key warnings

Photos, detailed wiring, connector pinouts, and polished step-by-step procedures may be added later and must not block release of usable key data.

## Current priority

1. Finish Ford Locksmith Cards and live JSON.
2. Map tool IDs.
3. Make the app display the completed data.
4. Test Ford on-device.
5. Move to the next manufacturer using this exact workflow.

## Prohibited direction changes

Until Ford is usable in the app, do not:

- Redesign the database structure
- Create more shared-reference databases
- Build photo libraries as a priority
- Generate empty model folders and call them complete
- Mark structure validation as technical validation
- Replace researched data with placeholders
- Start another manufacturer

## Definition of complete for the first usable release

A Ford generation is complete when a locksmith can quickly determine:

1. Which key or remote is required
2. Which blade is required
3. Which transponder is required
4. Which frequency is required
5. Useful OEM/stock part numbers
6. Whether Add Key is possible
7. Whether AKL is possible
8. Whether the job is OBD, online, bench, EEPROM, or module-based
9. Which owned/supported tools can perform each operation
10. Any important UK-specific warning

Photos are not required for this definition of complete.
