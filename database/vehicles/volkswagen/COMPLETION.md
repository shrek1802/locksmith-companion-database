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
- Architecture matrix: **ALL REQUESTED BATCHES RECORDED; TECHNICAL EVIDENCE OPEN**

## Architecture batch audit

| Batch | Structural gate | Matrix coverage | Technical disposition |
|---|---:|---:|---|
| MQB Passenger | Pass | 20 separate UK/RHD keyed or KESSY records | Research Required pending exact fitted-hardware and current application evidence |
| MQB Commercial | Pass | 6 separate UK/RHD keyed or KESSY records | Research Required pending exact fitted-hardware and current application evidence |
| PQ Platform | Pass | 10 separate UK/RHD keyed or KESSY records | Research Required except the existing source-backed Immo 4D family |
| Legacy | Pass | 9 separate UK/RHD keyed or KESSY records | Research Required pending generation splits and RHD module evidence |
| MEB | Pass | 4 UK/RHD keyless records | Research Required pending authorised procedure and RHD location evidence |

Matrix evidence is deliberately scoped to model, generation and architecture context. It does not verify locksmith procedures, tool support, pinouts or UK RHD component locations.

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
| Golf | Pass | Pass | Audit started | Pending | Research in progress |
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

## Golf audit findings

Golf currently contains six UK/RHD generation records:

- Golf Mk4, 1998–2004, keyed ignition
- Golf Mk5, 2004–2009, keyed ignition
- Golf Mk6, 2009–2013, keyed ignition
- Golf Mk7, 2013–2017, keyed or KESSY
- Golf Mk7.5, 2017–2020, keyed or KESSY
- Golf Mk8, 2020–present

The first audit pass confirms that all six generations have readable Add Key and All Keys Lost routes. The remaining work is technical verification rather than missing structure.

### Golf items still requiring evidence

- [ ] Split Golf Mk4 Immo2 and Immo3 coverage where exact build or cluster identification changes the route.
- [ ] Verify the supported Golf Mk5 and Mk6 dashboard families against current manufacturer application lists.
- [ ] Confirm every listed OBDSTAR cable or adapter against the exact dashboard processor and EEPROM family.
- [ ] Confirm every listed Autel Golf dashboard part number and operation against the current official coverage list.
- [ ] Keep MQB5A, MQB5B and MQB5C routes separate; do not infer support from model year alone.
- [ ] Confirm keyed and KESSY procedures separately for Golf Mk7 and Mk7.5.
- [ ] Confirm APB300 working-key routes by exact key and platform before upgrading any record from Conditional.
- [ ] Verify UK RHD OBD, dashboard, KESSY and access-start module locations.
- [ ] Verify bench connections and regulated-power requirements where a bench route is listed.
- [ ] Add or verify the required Golf photo records and assets.

No Golf record is upgraded to Fully Verified during this pass.

## Next audit order

1. Golf evidence and location verification
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
