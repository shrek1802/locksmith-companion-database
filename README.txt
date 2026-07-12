FORD FIESTA FIRST APP TEST

Upload/replace these paths in the DATABASE repository:

manifest.json
database/vehicles/ford/manifest.json
database/vehicles/ford/fiesta/

This package creates the locked Fiesta mini-database:

fiesta/
├── manifest.json
├── models.json
├── procedures.json
├── modules.json
├── wiring.json
├── service_functions.json
├── notes.json
└── photos.json

IMPORTANT

This is deliberately marked UI TEST ONLY.
It is designed to prove that:
- nested model downloads work
- Fiesta appears in the app
- Quick Job renders
- the custom OBD and EEPROM icons render
- all dashboard sections open

It must not be treated as verified workshop guidance yet.

TEST

1. Upload the files.
2. Run the database validator.
3. Open the new APK.
4. Tap Check database updates.
5. Open Ford → Fiesta Mk7 UI Test.
