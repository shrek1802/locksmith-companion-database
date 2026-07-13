# Evidence Hierarchy

**Version:** 1.0  
**Status:** Approved  
**Last updated:** 2026-07-14

## Purpose

This document ranks evidence used to approve vehicle, security and tool-support fields.

## Level 1 — Primary Authoritative Evidence

Highest priority:

- official vehicle-manufacturer workshop information;
- official owner/service documentation where relevant;
- official tool-manufacturer coverage lists or in-tool screenshots;
- official technical service bulletins;
- direct documented workshop evidence from the exact vehicle.

One strong Level 1 source may be sufficient when it directly proves the exact field and market/variant.

## Level 2 — Professional Technical Evidence

- recognised professional locksmith databases;
- specialist training material;
- established technical information providers;
- professional key catalogues for physical key details;
- multiple independent locksmith reports with matching vehicle details.

Normally require two agreeing Level 2 sources when no Level 1 source is available.

## Level 3 — Supporting Evidence

- reputable parts catalogues;
- OEM-part cross references;
- specialist retailer listings;
- professional forum discussions;
- workshop videos showing the exact vehicle and operation.

Use to support, not normally to prove, programming capability.

## Level 4 — Discovery-Only Evidence

- social media posts;
- anonymous forum claims;
- general blogs;
- marketplace listings;
- AI-generated summaries;
- uncited compatibility charts.

These may identify something to investigate but must not be the sole basis for a verified field.

## Field-Specific Rules

### Physical Key Data

Blade, frequency, button count and battery may use OEM part data plus reliable key catalogues.

### Transponder Data

Require exact part/chip evidence, tool identification, manufacturer documentation or matching professional sources. Do not infer chip type from appearance alone.

### Programming Capability

Require official tool coverage, an exact in-tool menu screenshot, manufacturer documentation or clear workshop evidence. A retailer saying a key "fits" does not prove Add Key or AKL support.

### Online/FDRS/SFD/SGW

Require official service information, tool documentation or exact workshop evidence. Do not infer from model year alone.

### Module Location

Prefer manufacturer workshop diagrams or clear UK RHD workshop evidence. LHD location data must not be relabelled as RHD without confirmation.

## Conflict Resolution

When sources disagree:

1. Check market, year, ignition type, trim, module number and build date.
2. Prefer the higher evidence level.
3. Look for a real security-generation split.
4. Record the conflict.
5. Use `verification_required` until resolved.

## Approval Threshold

A field may be marked `verified` when:

- a directly applicable Level 1 source proves it; or
- two independent Level 2 sources agree; or
- clear exact-vehicle workshop evidence confirms it and no stronger source conflicts.

## Evidence Record

For each approved field, retain:

- source title/provider;
- URL/document/tool path;
- date checked;
- market/vehicle applicability;
- field supported;
- evidence level;
- notes or limitations.
