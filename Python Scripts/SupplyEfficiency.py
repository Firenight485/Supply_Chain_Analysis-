import duckdb
import pandas as pd
from pathlib import Path

DATA_PATH = Path("supply_chain_data.csv")
OUTPUT_PATH = Path("product_cost_quality_summary.csv")

con = duckdb.connect(database=":memory:")

con.execute(f"""
    CREATE TABLE supply_chain AS
    SELECT * FROM read_csv_auto('{DATA_PATH.as_posix()}');
""")

query = """
WITH base AS (
    SELECT
        "Product type" AS product_type,
        COUNT(*) AS total_units,
        AVG("Manufacturing costs") AS avg_mfg_cost,
        AVG("Defect rates") AS avg_defect_rate,
        SUM(CASE WHEN "Inspection results" = 'Fail' THEN 1 ELSE 0 END) AS fail_count
    FROM supply_chain
    GROUP BY "Product type"
)
SELECT
    product_type,
    total_units,
    ROUND(avg_mfg_cost, 2) AS avg_mfg_cost,
    ROUND(avg_defect_rate, 2) AS avg_defect_rate,
    ROUND((fail_count * avg_mfg_cost), 2) AS est_defect_cost,
    ROUND((avg_defect_rate * avg_mfg_cost), 2) AS expected_quality_cost_per_unit,
    ROUND((avg_defect_rate * avg_mfg_cost * total_units), 2) AS total_expected_quality_cost
FROM base
ORDER BY total_expected_quality_cost DESC;
"""

df = con.execute(query).df()
print(df)

df.to_csv(OUTPUT_PATH, index=False)
print(f"\nSaved cost summary table to: {OUTPUT_PATH.resolve()}")