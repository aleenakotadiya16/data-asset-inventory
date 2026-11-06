# Data asset inventory

Personal practice project. The catalog is synthetic. It is not a UT Southwestern inventory and it does not contain real datasets.

The fields follow the same ideas as OpenMetadata and DataHub: an inventory of data assets, an owner, a steward, a sensitivity classification, and a short business glossary. This repository does not include those platforms.

Each of the 24 assets has an owner, a steward, a sensitivity label (`Public`, `Internal`, `Confidential`, or `Restricted-PHI`), a criticality, a source system, and an optional agreement (`DUA`, `DUSA`, or `DTA`) with an expiry date.

## Run

```bash
python inventory.py
streamlit run app.py
```

`python inventory.py` rebuilds `catalog.duckdb` and prints three figures, measured on 2026-11-06:

- percent of assets with a sensitivity label
- percent of assets that have no owner
- percent of assets that have an agreement and whose agreement expired before that date

## Test

```bash
python -m pytest test_inventory.py
```
