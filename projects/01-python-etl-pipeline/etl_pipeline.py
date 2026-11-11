"""Local CSV ETL demo: extract, clean, validate, and write curated records."""

import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "raw" / "orders.csv"
OUTPUT_DIR = BASE_DIR / "data" / "processed"
CLEAN_FILE = OUTPUT_DIR / "clean_orders.csv"
REJECTED_FILE = OUTPUT_DIR / "rejected_orders.csv"

OUTPUT_FIELDS = ["order_id", "customer", "order_date", "quantity", "unit_price", "total"]


def parse_order(row):
    """Normalize and validate one source row; return a clean record."""
    order_id = (row.get("order_id") or "").strip()
    customer = " ".join((row.get("customer") or "").split())
    order_date = (row.get("order_date") or "").strip()

    if not order_id or not customer or not order_date:
        raise ValueError("order_id, customer, and order_date are required")

    parsed_date = datetime.strptime(order_date, "%Y-%m-%d").date()
    quantity = int((row.get("quantity") or "").strip())
    unit_price = Decimal((row.get("unit_price") or "").strip())

    if quantity <= 0:
        raise ValueError("quantity must be greater than zero")
    if unit_price < 0:
        raise ValueError("unit_price cannot be negative")

    total = unit_price * quantity
    return {
        "order_id": order_id,
        "customer": customer,
        "order_date": parsed_date.isoformat(),
        "quantity": quantity,
        "unit_price": f"{unit_price:.2f}",
        "total": f"{total:.2f}",
    }


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run_pipeline():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    clean_rows, rejected_rows, seen_ids = [], [], set()

    with INPUT_FILE.open("r", newline="", encoding="utf-8") as handle:
        for line_number, source_row in enumerate(csv.DictReader(handle), start=2):
            try:
                record = parse_order(source_row)
                if record["order_id"] in seen_ids:
                    raise ValueError("duplicate order_id")
                seen_ids.add(record["order_id"])
                clean_rows.append(record)
            except (ValueError, InvalidOperation) as exc:
                rejected_rows.append({
                    "line_number": line_number,
                    "reason": str(exc),
                    "source_row": repr(source_row),
                })

    write_csv(CLEAN_FILE, clean_rows, OUTPUT_FIELDS)
    write_csv(REJECTED_FILE, rejected_rows, ["line_number", "reason", "source_row"])

    print(f"Rows loaded: {len(clean_rows)}")
    print(f"Rows rejected: {len(rejected_rows)}")
    print(f"Clean output: {CLEAN_FILE}")
    print(f"Rejected output: {REJECTED_FILE}")


if __name__ == "__main__":
    run_pipeline()
