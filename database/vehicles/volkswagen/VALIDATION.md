# Volkswagen validation rules

Volkswagen data is limited to the UK market and right-hand-drive vehicles.

The automated validator checks:

- every model declared by the Volkswagen manifest has the complete eight-file model structure;
- model IDs, model versions and manifest references are synchronised;
- the root manifests record the same Volkswagen version as the manufacturer manifest;
- vehicle records remain UK and RHD;
- procedure files use readable records under a top-level `items` object;
- both `add_key` and `all_keys_lost` are present for each procedure generation;
- raw `PROC_...` placeholders are rejected;
- procedure statuses use the approved vocabulary.

The validator does not treat technical claims as verified. Unconfirmed tool, module, processor, online-access or security-system information must remain marked `conditional`, `verification_required` or `research_required` until properly checked.
