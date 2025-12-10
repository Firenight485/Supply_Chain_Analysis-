import duckdb
import pandas as pd
from pathlib import Path

DATA_PATH = Path("supply_chain_data.csv")
OUTPUT_PATH = Path("product_type_quality_summary.csv")

con = duckdb.connect(database=":memory:")

# Load raw CSV into DuckDB
con.execute(f"""
    CREATE TABLE supply_chain AS
    SELECT * FROM read_csv_auto('{DATA_PATH.as_posix()}');
""")

query = """
WITH base AS (
    SELECT
        "Product type" AS product_type,
        COUNT(*) AS total_records,
        -- inspection outcome counts
        SUM(CASE WHEN "Inspection results" = 'Fail' THEN 1 ELSE 0 END) AS fail_count,
        SUM(CASE WHEN "Inspection results" = 'Pass' THEN 1 ELSE 0 END) AS pass_count,
        SUM(CASE WHEN "Inspection results" = 'Pending' THEN 1 ELSE 0 END) AS pending_count,
        -- core quality metrics
        AVG("Defect rates") AS avg_defect_rate,
        AVG("Manufacturing lead time") AS avg_mfg_lead_time,
        AVG("Lead times") AS avg_supplier_lead_time,
        AVG("Manufacturing costs") AS avg_mfg_cost
    FROM supply_chain
    GROUP BY "Product type"
)
SELECT
    product_type,
    total_records,
    fail_count,
    pass_count,
    pending_count,
    ROUND(100.0 * fail_count / NULLIF(total_records, 0), 2) AS fail_rate_pct,
    ROUND(100.0 * pass_count / NULLIF(total_records, 0), 2) AS pass_rate_pct,
    ROUND(avg_defect_rate, 2) AS avg_defect_rate,
    ROUND(avg_mfg_lead_time, 2) AS avg_mfg_lead_time,
    ROUND(avg_supplier_lead_time, 2) AS avg_supplier_lead_time,
    ROUND(avg_mfg_cost, 2) AS avg_mfg_cost,
    -- simple derived metrics for dashboards
    ROUND(fail_count * avg_mfg_cost, 2) AS est_defect_cost,
    ROUND(avg_defect_rate * avg_mfg_lead_time, 2) AS defect_risk_score
FROM base
ORDER BY fail_rate_pct DESC;
"""

result = con.execute(query).df()
print(result)

result.to_csv(OUTPUT_PATH, index=False)
print(f"\nSaved quality summary table to: {OUTPUT_PATH.resolve()}")