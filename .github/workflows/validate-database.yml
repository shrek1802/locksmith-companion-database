name: Validate Database

on:
  workflow_dispatch:
  push:
    branches:
      - main
    paths:
      - "**/*.json"
      - "scripts/validate_database.py"
      - ".github/workflows/validate-database.yml"
  pull_request:
    paths:
      - "**/*.json"
      - "scripts/validate_database.py"
      - ".github/workflows/validate-database.yml"

permissions:
  contents: read

concurrency:
  group: validate-database-${{ github.ref }}
  cancel-in-progress: true

jobs:
  validate:
    name: Check JSON database
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Validate database
        run: python scripts/validate_database.py

      - name: Upload validation report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: database-validation-${{ github.run_number }}-${{ github.run_attempt }}
          path: database-validation-report.txt
          if-no-files-found: error
          overwrite: true
