import duckdb
import pandas as pd
from pathlib import Path

DATA_PATH = Path("supply_chain_data.csv")
OUTPUT_PATH = Path("product_type_summary.csv")


con = duckdb.connect(database=":memory:")

con.execute(f"""
    CREATE TABLE supply_chain AS
    SELECT * FROM read_csv_auto('{DATA_PATH.as_posix()}');
""")

query = """
    SELECT
        "Product type" AS product_type,
        SUM("Revenue generated") AS total_revenue,
        SUM("Number of products sold") AS total_units_sold,
        AVG("Price") AS avg_price,
        SUM("Revenue generated") / NULLIF(SUM("Number of products sold"), 0) AS revenue_per_unit,
        SUM("Revenue generated") / NULLIF(COUNT(DISTINCT "SKU"), 0) AS revenue_per_sku,
        ROUND(
            100.0 * SUM("Revenue generated")
            / SUM(SUM("Revenue generated")) OVER (),
            2
        ) AS pct_of_total_revenue
    FROM supply_chain
    GROUP BY "Product type"
    ORDER BY total_revenue DESC;
"""

result = con.execute(query).df()

print(result)

result.to_csv(OUTPUT_PATH, index=False)
print(f"\nSaved summary table to: {OUTPUT_PATH.resolve()}")