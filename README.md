# 🏗️ End-to-End Sales Analytics Pipeline

A production-style data engineering pipeline built on the modern DE stack,
using the Olist Brazilian E-Commerce dataset.

## 🏛️ Architecture
```
Olist CSV Files (Source)
        ↓
Python + Pandas (Extract & Clean)
        ↓
AWS S3 (Data Lake - raw/)
        ↓
Great Expectations (Quality Gate)
        ↓
DuckDB (Data Warehouse)
        ↓
dbt (Transform: staging → marts)
        ↓
mart_revenue_by_city (Analytics Ready)

Apache Airflow orchestrates all steps ↑
```

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python + Pandas | Extraction & basic transformation |
| Apache Airflow 2.10.4 | Pipeline orchestration & scheduling |
| AWS S3 | Data lake (raw storage) |
| DuckDB | Columnar data warehouse |
| dbt 1.11.7 | SQL transformation layer |
| AWS EC2 (Ubuntu) | Cloud compute |
| Git + GitHub | Version control |

## 📁 Project Structure
```
de-project/
├── scripts/
│   ├── extract.py            # Extract CSVs → clean → upload to S3
│   ├── quality_checks.py     # Data quality gate (nulls, counts, freshness)
│   └── load_to_warehouse.py  # Load Parquet from S3 → DuckDB
│
├── dags/
│   └── sales_pipeline.py     # Airflow DAG orchestrating all tasks
│
├── dbt_project/
│   ├── models/
│   │   ├── staging/          # One model per source table
│   │   │   ├── stg_orders.sql
│   │   │   ├── stg_customers.sql
│   │   │   ├── stg_payments.sql
│   │   │   ├── stg_products.sql
│   │   │   └── schema.yml    # dbt tests
│   │   └── marts/
│   │       └── mart_revenue_by_city.sql  # Final analytics table
│   └── dbt_project.yml
│
└── README.md
```

## 🔁 Pipeline Flow

### 1. Extract (`extract.py`)
- Loads 4 Olist CSV datasets using Pandas
- Cleans data: removes duplicates, parses dates, filters nulls
- Converts to Parquet format and uploads to AWS S3

### 2. Quality Gate (`quality_checks.py`)
- Reads Parquet files directly from S3
- Runs 4 types of checks on every dataset:
  - Null checks on primary keys
  - Row count validation (min/max bounds)
  - Freshness check (data recency)
  - Business rule validation (positive payment values)
- Pipeline halts if any check fails — bad data never reaches warehouse

### 3. Load (`load_to_warehouse.py`)
- Reads validated Parquet files from S3
- Loads into DuckDB columnar warehouse
- Creates raw schema with 4 tables:
  - raw.orders (99,441 rows)
  - raw.customers (99,441 rows)
  - raw.payments (103,886 rows)
  - raw.products (32,951 rows)

### 4. Transform (dbt)
- Staging models: clean and rename raw tables
- Mart model: joins orders + customers + payments
- Produces mart_revenue_by_city with:
  - Total orders per city per month
  - Total revenue per city per month
  - Average order value per city per month

## ✅ Data Quality

Quality is enforced at two layers:

**Ingestion layer** (`quality_checks.py`):
- Row count bounds (catches data loss at source)
- Freshness checks (catches stale data)
- Null checks on primary keys
- Business rule validation

**Transformation layer** (dbt tests):
- Uniqueness tests on all primary keys
- Not-null tests on all primary keys
- 8 tests total — all passing ✅

## 🚀 How to Run

### Prerequisites
- AWS account with S3 bucket
- EC2 Ubuntu instance (t2.micro)
- Python 3.12+

### Setup
```bash
# Clone repo
git clone https://github.com/YOUR-USERNAME/de-portfolio-project.git

# Create virtual environment
python3 -m venv de-project-env
source de-project-env/bin/activate

# Install dependencies
pip install pandas boto3 pyarrow duckdb dbt-duckdb apache-airflow==2.10.4
```

### Run Pipeline
```bash
# Manual run
python scripts/extract.py
python scripts/quality_checks.py
python scripts/load_to_warehouse.py

# dbt transformation
cd dbt_project
dbt run
dbt test

# Or trigger via Airflow UI
airflow webserver --port 8080 -D
airflow scheduler -D
```

## 📊 Sample Output
```sql
-- mart_revenue_by_city (top 5 cities by revenue)
SELECT city, month, total_orders, total_revenue
FROM mart_revenue_by_city
ORDER BY total_revenue DESC
LIMIT 5;

city          | month   | total_orders | total_revenue
--------------|---------|--------------|---------------
sao paulo     | 2018-03 | 1,245        | 187,432.50
rio de janeiro| 2018-03 | 876          | 134,218.75
belo horizonte| 2018-02 | 543          | 98,432.00
brasilia      | 2018-01 | 421          | 76,543.25
curitiba      | 2018-03 | 398          | 65,432.10
```

## 🔮 Future Improvements
- Add dbt task to Airflow DAG for full automation
- Migrate from DuckDB to Amazon Redshift for production scale
- Add data visualisation layer (Apache Superset / Metabase)
- Implement incremental dbt models for efficiency
- Add Great Expectations for advanced quality checks
- Set up CI/CD with GitHub Actions

## 👩‍💻 Author
Built as a portfolio project during transition from
Software Testing to Data Engineering.
