# 04 - Azure End-to-End Data Engineering Pipeline

A portfolio project that demonstrates an Azure-style batch data pipeline using Azure Data Factory (ADF), Azure Data Lake Storage Gen2 (ADLS Gen2), and a Bronze / Silver / Gold data organization.

The repository includes a local runnable version of the transformations, sample source data, a Gold-layer SQL query, and an ADF pipeline definition template.

> **Important:** This is a portfolio implementation and configuration template. It does not claim that Azure resources have been provisioned or that a cloud pipeline has been deployed. The local Python run can be completed without an Azure subscription.

## Architecture

```text
Source CSV
   |
   v
ADF Copy activity
   |
   v
ADLS Gen2 - Bronze (raw landing copy)
   |
   v
Databricks notebook / Spark transformation
   |
   +------> Silver (cleaned, typed, deduplicated records)
   |
   +------> Quarantine (invalid records + reason)
   |
   v
Gold (daily sales summary)
   |
   v
Power BI / reporting
```

## Medallion layers

| Layer | Purpose | Example path |
|---|---|---|
| Bronze | Preserve source data with minimal changes | `/bronze/orders/` |
| Silver | Clean, validate, standardize, and deduplicate | `/silver/orders/` |
| Gold | Business-ready aggregates for reporting | `/gold/daily_sales/` |
| Quarantine | Keep rejected rows for investigation | `/quarantine/orders/` |

## Repository contents

- `data/raw/orders.csv` - fictional sample order data with a few quality issues
- `local_pipeline.py` - runnable local ETL demonstration using Python's standard library
- `sql/gold_daily_sales.sql` - example Gold-layer aggregation
- `adf/pipeline_orders.json` - ADF pipeline definition template with dataset and linked-service placeholders

## Run locally

Requirements: Python 3.10 or later. No external Python packages are required.

From this directory:

```bash
python local_pipeline.py
```

The script creates:
- `output/bronze/orders.csv`
- `output/silver/orders.csv`
- `output/gold/daily_sales.csv`
- `output/quarantine/orders.csv`

The sample contains a duplicate order ID, a missing customer, an invalid date, and a non-positive quantity to demonstrate validation and quarantine handling.

## Azure implementation outline

1. Create an ADLS Gen2 storage account and a container such as `datalake`.
2. Create folders for `landing`, `bronze`, `silver`, `gold`, and `quarantine`.
3. Upload the sample CSV to `landing/orders/`.
4. In Azure Data Factory, create a linked service for ADLS Gen2 using managed identity where possible.
5. Create delimited-text datasets for the landing and Bronze locations. Use the same column structure as the sample CSV.
6. Configure the ADF pipeline in `adf/pipeline_orders.json` as a starting reference. Replace the placeholder dataset and linked-service names with the names in your environment.
7. Configure the referenced Databricks linked service and notebook, or replace that activity with your chosen Spark compute step. The notebook should implement the same cleaning, deduplication, quarantine, and Gold aggregation rules as the local example.
8. Grant the ADF managed identity the required storage permissions. Avoid putting account keys, passwords, or tokens in source control.
9. Trigger the pipeline and verify row counts and output files in each layer.
10. Connect the Gold output to Power BI or query it with your preferred analytics engine.

## Data quality rules

- Required: `order_id`, `customer`, `order_date`
- `order_date` must use `YYYY-MM-DD`
- `quantity` must be a positive integer
- `unit_price` must be a non-negative decimal
- Keep one record per `order_id`; duplicate records are quarantined
- Invalid records are retained separately with a rejection reason

## Skills demonstrated

Azure Data Factory concepts, ADLS Gen2 folder design, ETL/ELT, Medallion architecture, Python, SQL, data quality, deduplication, and pipeline documentation.

## Next improvements

- Implement the Spark notebook used by the ADF pipeline
- Add automated tests and structured pipeline logging
- Add incremental loads using a watermark
- Add schema evolution and reject-rate monitoring
- Publish a Power BI report using the Gold output
