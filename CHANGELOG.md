# Database Changelog

## 2026.07.19-structured-key-profiles-2

- Added `database/database-update.json`, a single 8.61 MB indexed JSON package containing the complete published database.
- Added package URL, SHA-256, size, format and record counts to the root manifest.
- Retained all raw JSON files for backwards compatibility while making the consolidated package the normal app update path.

## 2026.07.19-structured-key-profiles-1

- Rebuilt the raw-file update hierarchy for all 53 UK manufacturers, 733 models and 1,499 vehicle records.
- Published the seven-field structured key-profile contract and canonical blade, transponder and chip catalogues.
- Regenerated manufacturer/model versions, component checksums and the complete database package index.
- Delivery remains the existing `main/manifest.json` plus individual raw JSON files; no competing ZIP updater was introduced.

## 2026.07.05-cumulative-asia-1

- Expanded Toyota/Lexus/Honda/Mazda/Hyundai/Kia/Suzuki/Subaru generation-key records.
- Rebuilt manifest from actual manufacturer files.
- Single cumulative pack only.


## 2026.07.05-cumulative-alliance-1

- Expanded Renault generation/key-system records.
- Expanded Dacia generation/key-system records.
- Expanded Nissan generation/key-system records.
- Expanded Mitsubishi generation/key-system records.
- Rebuilt manifest from actual manufacturer files.
- Single cumulative pack only.


## 2026.07.05-cumulative-mercedes-smart-1

- Built from latest uploaded working repository.
- Added/expanded Mercedes-Benz generation/key-system records.
- Added/expanded Smart generation/key-system records.
- Rebuilt manifest from actual manufacturer files.
- Single cumulative pack only; upload as database_pack.zip.


## 2026.07.04-merged-all-packs-1

- Merged all available database_pack*.zip files into one pack.
- Rebuilt manifest.json so all included manufacturer files are listed.
- Prevents the last uploaded pack from overwriting the manifest for earlier packs.
