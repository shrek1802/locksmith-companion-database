DATABASE ROOT MIGRATION

Upload/replace these files in the database repository:

manifest.json
database/vehicles/manifest.json
database/vehicles/ford/manifest.json

IMPORTANT:
- Keep manifest.json at the repository root.
- The app can keep using:
  https://raw.githubusercontent.com/shrek1802/locksmith-companion-database/main/manifest.json
- The root manifest now points into:
  database/vehicles/ford/manifest.json
- The Ford manifest uses the `models` object expected by the current app updater.
- It is intentionally empty until the first verified Fiesta model JSON is ready.

No app code needs changing just for moving the remote files into database/.
The manifest path handles the move.
