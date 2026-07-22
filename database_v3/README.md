# Locksmith Companion Database V3

Database V3 stores reusable locksmith knowledge as components and compiles small vehicle records into the complete JSON shape consumed by the app.

## Layout

- `components/` reusable platforms, immobilisers, keys, blades, transponders, procedures, tool coverage and locations
- `vehicles/` small UK/RHD vehicle records containing component references and model-specific overrides
- `schema/` JSON schemas
- `scripts/compile_v3.py` resolver/compiler
- `compiled/` generated app-ready JSON (not hand edited)

## Pilot

The first pilot covers four related MQB vehicles:

- Volkswagen Golf Mk7
- Audi A3 8V
- SEAT Leon 5F
- Skoda Octavia 5E

## Compile

```bash
python database_v3/scripts/compile_v3.py
```

The compiler validates references, deep-merges components in a fixed order, applies vehicle overrides last, and writes `database_v3/compiled/vag_mqb_pilot.json`.

Unknown or unverified claims must remain `null` or `unknown`; the compiler never turns missing data into verified data.
