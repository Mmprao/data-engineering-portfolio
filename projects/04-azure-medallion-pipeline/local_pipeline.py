"""Local demonstration of a Bronze / Silver / Gold batch pipeline.

Uses only the Python standard library. It does not connect to Azure.
"""

import csv
import shutil
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "data" / "raw" / "orders.csv"
OUTPUT = BASE / "output"
BRONZE = OUTPUT / "bronze" / "orders.csv"
SILVER = OUTPUT / "silver" / "orders.csv"
GOLD = OUTPUT / "gold" / "daily_sales.csv"
QUARANTINE = OUTPUT / "quarantine" / "orders.csv"

SILVER_FIELDS = ["order_id", "customer", "order_date", "product", "quantity", "unit_price", "total"]
QUARANTINE_FIELDS = ["source_row", "rejection_reason"]
GOLD_FIELDS = ["order_date", "order_count", "units_sold", "revenue"]


def read_rows(path):
    with path.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def write_rows(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def transform_row(source):
    order_id = (source.get("order_id") or "").strip()
    customer = " ".join((source.get("customer") or "").split())
    product = " ".join((source.get("product") or "").split())
    if not order_id or not customer or not product:
        raise ValueError("order_id, customer, and product are required")

    order_date = datetime.strptime(
        (source.get("order_date") or "").strip(), "%Y-%m-%d"
    ).date().isoformat()
    quantity = int((source.get("quantity") or "").strip())
    unit_price = Decimal((source.get("unit_price") or "").strip())

    if quantity <= 0:
        raise ValueError("quantity must be greater than zero")
    if unit_price < 0:
        raise ValueError("unit_price cannot be negative")

    total = unit_price * quantity
    return {
        "order_id": order_id,
        "customer": customer,
        "order_date": order_date,
        "product": product,
        "quantity": quantity,
        "unit_price": f"{unit_price:.2f}",
        "total": f"{total:.2f}",
    }


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Sample source file not found: {SOURCE}")

    # Bronze: preserve an unchanged copy of the source file.
    BRONZE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE, BRONZE)

    silver_rows = []
    quarantine_rows = []
    seen_order_ids = set()

    for line_number, row in enumerate(read_rows(BRONZE), start=2):
        try:
            clean = transform_row(row)
            if clean["order_id"] in seen_order_ids:
                raise ValueError("duplicate order_id")
            seen_order_ids.add(clean["order_id"])
            silver_rows.append(clean)
        except (ValueError, InvalidOperation) as error:
            quarantine_rows.append({
                "source_row": line_number,
                "rejection_reason": str(error),
            })

    # Silver: standardized and validated detail records.
    write_rows(SILVER, silver_rows, SILVER_FIELDS)
    write_rows(QUARANTINE, quarantine_rows, QUARANTINE_FIELDS)

    # Gold: daily business summary derived only from accepted Silver records.
    daily = defaultdict(lambda: {"order_ids": set(), "units": 0, "revenue": Decimal("0.00")})
    for row in silver_rows:
        bucket = daily[row["order_date"]]
        bucket["order_ids"].add(row["order_id"])
        bucket["units"] += int(row["quantity"])
        bucket["revenue"] += Decimal(row["total"])

    gold_rows = []
    for order_date, values in sorted(daily.items()):
        gold_rows.append({
            "order_date": order_date,
            "order_count": len(values["order_ids"]),
            "units_sold": values["units"],
            "revenue": f'{values["revenue"]:.2f}',
        })
    write_rows(GOLD, gold_rows, GOLD_FIELDS)

    print(f"Bronze source rows: {len(read_rows(BRONZE))}")
    print(f"Silver accepted rows: {len(silver_rows)}")
    print(f"Quarantined rows: {len(quarantine_rows)}")
    print(f"Gold daily summaries: {len(gold_rows)}")
    print(f"Output directory: {OUTPUT}")


if __name__ == "__main__":
    main()
