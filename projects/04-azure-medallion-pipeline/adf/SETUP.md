# Azure Data Factory template setup

The JSON file in this folder is a starting pipeline definition, not a complete ARM deployment package. It references resources that you must create and configure in your own Azure environment.

## Required ADF resources

Create these resources before importing or recreating the pipeline:

- Linked service for ADLS Gen2, using the storage account and an appropriate managed identity or approved authentication method
- Dataset `ds_landing_orders_csv` pointing to the landing CSV folder and file format
- Dataset `ds_bronze_orders_csv` pointing to the Bronze folder and the same CSV format
- Linked service `ls_azure_databricks` connected to your Databricks workspace
- Databricks notebook at `/Shared/portfolio/transform_orders`

## Before running

1. Replace `<storage-account>` with your storage account name in the notebook parameters.
2. Confirm the container name and directory paths match your ADLS Gen2 layout.
3. Configure access for the ADF managed identity and Databricks identity.
4. Implement the referenced notebook so it reads Bronze data and writes Silver, Gold, and Quarantine outputs.
5. Validate the pipeline in a development environment before triggering it.

Do not commit connection strings, access keys, client secrets, personal access tokens, or other credentials to GitHub. Prefer managed identity and secret stores such as Azure Key Vault.
