# 01 - Python ETL Pipeline

A small end-to-end ETL example that reads raw order data, validates and cleans records, then writes curated output files.

## Pipeline

1. **Extract:** Read the source CSV file.
2. **Transform:** Normalize text, parse dates and numeric values, and identify invalid rows.
3. **Validate:** Check required fields, positive quantities, valid prices, and duplicate order IDs.
4. **Load:** Write clean records and rejected records to separate output files.

The folders represent a simple local Bronze-to-Silver flow. They are inspired by a Medallion architecture, but this project does not deploy Azure resources.

## Requirements

- Python 3.10+
- No third-party packages required

## Run

From this project folder:

```bash
python etl_pipeline.py
```

The script creates output files under `data/processed/`.

## Example data

The input file is `data/raw/orders.csv`. It intentionally includes whitespace, a duplicate, and an invalid row so the validation logic can be demonstrated.

## Possible extensions

- Store raw and curated data in Azure Data Lake Storage Gen2
- Orchestrate the pipeline with Azure Data Factory
- Add automated tests and structured logging
- Load curated records into a SQL database or Microsoft Fabric Lakehouse
