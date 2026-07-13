# Security Generations

**Version:** 1.0  
**Status:** Approved  
**Last updated:** 2026-07-14

## Purpose

This document defines the naming system for immobiliser and key-programming security families used by the Locksmith Companion Database.

A security-generation identifier describes the underlying programming architecture. It does not replace the vehicle badge name shown in the app.

## Naming Format

Use uppercase identifiers:

`<MANUFACTURER_OR_FAMILY>_<SYSTEM>_<GENERATION_OR_PLATFORM>`

Examples:

- `FORD_PATS_EARLY`
- `FORD_PATS_BCM`
- `FORD_SMARTKEY_BCM`
- `FIAT_CODE2`
- `VW_IMMO4`
- `VW_MQB_IMMO5`
- `VW_MEB`
- `BMW_CAS3`
- `BMW_FEM`
- `BMW_BDC`
- `MERCEDES_FBS3`
- `MERCEDES_FBS4`
- `PSA_BSI`
- `RENAULT_UCH`

Do not create a new identifier merely because a model facelifted. Create one only when locksmith-relevant architecture changes.

## Required Profile Fields

Each security profile should document:

- profile ID;
- manufacturer or source architecture;
- immobiliser family;
- programming controller/module;
- keyed/passive applicability;
- normal programming route;
- security access type;
- online/gateway requirement;
- EEPROM or bench requirement;
- tool-support notes;
- known limitations;
- evidence status.

## Ford Families

### `FORD_PATS_EARLY`

Early transponder-era Ford PATS systems. Exact key, module and programming route must be verified by model and year.

### `FORD_PATS_CLUSTER`

PATS architecture where the instrument cluster participates directly in immobiliser/key programming.

### `FORD_PATS_BCM`

Ford BCM-controlled PATS used across many later keyed vehicles. Exact software generation and security access remain model/build dependent.

### `FORD_SMARTKEY_BCM`

Ford passive-start/Intelligent Access architecture controlled through BCM-related systems.

### `FORD_FDRS_SECURITY`

Ford vehicles or operations where authorised FDRS-based security access is required. This profile must never be assigned from model year alone.

## Volkswagen Families

### `VW_IMMO2`

Early Volkswagen immobiliser generation. Exact PIN and module route varies by platform.

### `VW_IMMO3`

Volkswagen immobiliser generation commonly involving cluster/ECU/key adaptation.

### `VW_IMMO4`

Later VAG immobiliser architecture including platform-specific component-security data.

### `VW_MQB_IMMO5`

MQB/Immo 5 architecture. Tool, online and component-data requirements must be recorded per exact vehicle and operation.

### `VW_MEB`

Volkswagen MEB electric-vehicle architecture. Do not assume normal MQB procedures apply.

## Fiat Families

### `FIAT_CODE1`

Early Fiat CODE architecture.

### `FIAT_CODE2`

Body-computer-based Fiat CODE architecture used across many later Fiat-derived vehicles.

### `FIAT_CODE3`

Later Fiat/Stellantis security architecture requiring separate verification.

## BMW Families

- `BMW_EWS`
- `BMW_CAS2`
- `BMW_CAS3`
- `BMW_CAS3_PLUS`
- `BMW_CAS4`
- `BMW_FEM`
- `BMW_BDC`

Each profile must distinguish add-key, all-keys-lost, ISN/security-data and bench requirements.

## Mercedes-Benz Families

- `MERCEDES_DAS2`
- `MERCEDES_FBS3`
- `MERCEDES_FBS4`

FBS4 must not inherit FBS3 programming assumptions.

## PSA/Stellantis Families

- `PSA_BSI_EARLY`
- `PSA_BSI_CAN`
- `STELLANTIS_SGW`

Exact PIN, gateway and online requirements must be recorded by platform.

## Renault/Dacia Families

- `RENAULT_UCH_EARLY`
- `RENAULT_UCH_CAN`
- `RENAULT_HFM_SMARTKEY`

## Mazda/Nissan Families

Use platform-specific profiles such as:

- `MAZDA_PATS_SHARED`
- `MAZDA_SMARTKEY`
- `NISSAN_NATS`
- `NISSAN_BCM_SMARTKEY`

Do not label a shared-platform Ford as Ford PATS when the underlying system is Mazda or Nissan.

## Profile Assignment Rule

A vehicle record may reference only a profile supported by evidence for that exact model/variant range.

When evidence is incomplete, use:

- `security_generation: verification_required`

Do not invent a generation number to make records appear complete.

## Maintenance

New security profiles require:

1. evidence of a real locksmith-relevant architectural difference;
2. an entry in `Docs/DESIGN_DECISIONS.md`;
3. updates to validation/schema documentation;
4. review of all vehicles that may use the profile.
