"""Local PySpark CSV transformation and data quality demonstration."""

from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum as spark_sum, trim, to_date
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, DecimalType
)

BASE_DIR = Path(__file__).resolve().parent
INPUT_PATH = str(BASE_DIR.parent / "01-python-etl-pipeline" / "data" / "raw" / "orders.csv")
OUTPUT_DIR = str(BASE_DIR / "output")

SCHEMA = StructType([
    StructField("order_id", StringType(), True),
    StructField("customer", StringType(), True),
    StructField("order_date", StringType(), True),
    StructField("quantity", StringType(), True),
    StructField("unit_price", StringType(), True),
])


def main():
    spark = (
        SparkSession.builder
        .appName("PortfolioOrderProcessing")
        .master("local[*]")
        .getOrCreate()
    )

    try:
        raw_df = spark.read.option("header", True).schema(SCHEMA).csv(INPUT_PATH)

        typed_df = (
            raw_df
            .withColumn("order_id", trim(col("order_id")))
            .withColumn("customer", trim(col("customer")))
            .withColumn("order_date", to_date(col("order_date"), "yyyy-MM-dd"))
            .withColumn("quantity", col("quantity").cast(IntegerType()))
            .withColumn("unit_price", col("unit_price").cast(DecimalType(10, 2)))
        )

        valid_condition = (
            col("order_id").isNotNull()
            & (col("order_id") != "")
            & col("customer").isNotNull()
            & (col("customer") != "")
            & col("order_date").isNotNull()
            & (col("quantity") > 0)
            & (col("unit_price") >= 0)
        )

        valid_candidates = typed_df.filter(valid_condition)
        rejected_df = typed_df.filter(~valid_condition)

        # Keep the first occurrence of each order ID for this demonstration.
        from pyspark.sql import Window
        from pyspark.sql.functions import row_number

        dedupe_window = Window.partitionBy("order_id").orderBy("order_date")
        valid_df = (
            valid_candidates
            .withColumn("_row_num", row_number().over(dedupe_window))
            .filter(col("_row_num") == 1)
            .drop("_row_num")
            .withColumn("total", col("quantity") * col("unit_price"))
        )

        valid_df.write.mode("overwrite").option("header", True).csv(
            f"{OUTPUT_DIR}/silver_orders"
        )
        rejected_df.write.mode("overwrite").option("header", True).csv(
            f"{OUTPUT_DIR}/rejected_orders"
        )

        print("Valid order count:", valid_df.count())
        print("Rejected row count:", rejected_df.count())
        print("Revenue by customer:")
        valid_df.groupBy("customer").agg(
            spark_sum("total").alias("total_revenue"),
            count("*").alias("order_count"),
        ).orderBy(col("total_revenue").desc()).show(truncate=False)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
