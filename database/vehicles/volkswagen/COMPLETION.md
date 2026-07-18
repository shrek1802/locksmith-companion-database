# Volkswagen Database Completion

Updated: 2026-07-18

## Current gate status

- Dedicated Volkswagen structural validator: **PASS**
- Full repository database validator: **PASS**
- UK market declaration: **PASS**
- RHD declaration: **PASS**
- Required eight-file model structure: **PASS**
- JSON/schema consistency currently enforced by CI: **PASS**
- Technical locksmith verification: **IN PROGRESS**
- Manufacturer sign-off: **NOT YET COMPLETE**

Passing validation means the files are structurally consistent. It does not mean every technical claim, tool route, module location, wiring detail or photo has been independently verified.

## Definition of done

Volkswagen can only be marked complete when all of the following are true:

- [x] Every declared model has the required eight JSON files.
- [x] Both Volkswagen and full-database validators pass.
- [x] All records are restricted to the UK market and RHD vehicles.
- [x] No raw procedure placeholder IDs remain.
- [x] Every generation has readable Add Key and All Keys Lost records.
- [ ] Every generation has been technically reviewed against current primary or manufacturer documentation.
- [ ] Tool coverage is confirmed per exact generation/system rather than inferred from model year.
- [ ] Module, OBD, SGW, KESSY and immobiliser locations are verified for UK RHD vehicles.
- [ ] Wiring and bench connection data is verified where supplied.
- [ ] Photo records contain verified assets or remain clearly marked Research Required.
- [ ] All Verification Required and Research Required records have been reviewed.
- [ ] Final manufacturer status is changed only after technical sign-off.

## Model audit tracker

| Model | Structure | Procedures present | Technical review | Photos/locations | Final status |
|---|---:|---:|---:|---:|---|
| Amarok | Pass | Pass | Pending | Pending | Research in progress |
| Arteon | Pass | Pass | Pending | Pending | Research in progress |
| Beetle | Pass | Pass | Pending | Pending | Research in progress |
| Caddy | Pass | Pass | Pending | Pending | Research in progress |
| CC | Pass | Pass | Pending | Pending | Research in progress |
| Crafter | Pass | Pass | Pending | Pending | Research in progress |
| Eos | Pass | Pass | Pending | Pending | Research in progress |
| Golf | Pass | Pass | Partial | Pending | Research in progress |
| ID.3 | Pass | Pass | Pending | Pending | Research in progress |
| ID.4 | Pass | Pass | Pending | Pending | Research in progress |
| ID.5 | Pass | Pass | Pending | Pending | Research in progress |
| ID. Buzz | Pass | Pass | Pending | Pending | Research in progress |
| Jetta | Pass | Pass | Pending | Pending | Research in progress |
| Passat | Pass | Pass | Partial | Pending | Research in progress |
| Polo | Pass | Pass | Partial | Pending | Research in progress |
| Scirocco | Pass | Pass | Pending | Pending | Research in progress |
| Sharan | Pass | Pass | Pending | Pending | Research in progress |
| T-Cross | Pass | Pass | Pending | Pending | Research in progress |
| T-Roc | Pass | Pass | Pending | Pending | Research in progress |
| Taigo | Pass | Pass | Pending | Pending | Research in progress |
| Tiguan | Pass | Pass | Pending | Pending | Research in progress |
| Touareg | Pass | Pass | Pending | Pending | Research in progress |
| Touran | Pass | Pass | Pending | Pending | Research in progress |
| Transporter | Pass | Pass | Pending | Pending | Research in progress |
| Up! | Pass | Pass | Pending | Pending | Research in progress |

## Next audit order

1. Golf
2. Passat
3. Polo
4. Caddy
5. Transporter
6. Crafter
7. Tiguan
8. Touran
9. Touareg
10. Remaining passenger models
11. MEB models

## Status rules

- **Research in progress**: records exist but technical review is incomplete.
- **Verification required**: a specific statement or route needs confirmation.
- **Conditional**: support depends on an exact dashboard, module, key type, software version or tool menu.
- **Fully verified**: only used after the relevant records have evidence and a completed technical audit.

Do not upgrade a model or manufacturer to Fully Verified merely because CI passes.