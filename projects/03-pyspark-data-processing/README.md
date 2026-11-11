# 03 - PySpark Data Processing

A local PySpark example that reads order records, applies DataFrame transformations, checks data quality, and separates valid and invalid records.

## Demonstrates

- Creating a Spark session
- Reading CSV data with an explicit schema
- Trimming and normalizing string columns
- Casting dates and numeric fields
- Filtering invalid records
- Removing duplicate order IDs
- Aggregating order totals

## Requirements

- Python 3.10+
- Java runtime supported by your chosen PySpark version
- Install dependencies with:

```bash
pip install -r requirements.txt
```

## Run

```bash
spark-submit process_orders.py
```

The script writes valid records and rejected records to local output folders. This is a local demonstration; it does not claim to run on a Spark cluster or Microsoft Fabric.

## Cloud extension

The same transformation pattern could be adapted to read Bronze data from ADLS Gen2 and write curated Silver/Gold outputs. That deployment would require an Azure subscription, storage configuration, identity permissions, and environment-specific settings.
