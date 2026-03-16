import boto3
import duckdb
import io
import os
import pandas as pd

#---------------CONFIG-------------------------------
BUCKET_NAME = 'de-project-olist-data'
DB_PATH = '/home/ubuntu/de-project/warehouse.duckdb'
#----------------------------------------------------

def read_parquet_from_s3(s3_key):
    """Read parquet file from S3 into a DataFrame"""
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=BUCKET_NAME, Key=s3_key)
    buffer = io.BytesIO(response['Body'].read())
    return pd.read_parquet(buffer)

def load_to_warehouse():
    print("Loading data into warehouse ...")

    # Connect to DuckDB (Creates the file if it doesn't exist)
    con = duckdb.connect(DB_PATH)

    # Create raw schema
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")

    # Load Orders
    print("Loading Orders....")
    orders = read_parquet_from_s3('raw/orders/orders.parquet')
    con.execute("DROP TABLE IF EXISTS raw.orders")
    con.execute("CREATE TABLE raw.orders AS SELECT * FROM orders")
    count = con.execute("SELECT COUNT(*) FROM raw.orders").fetchone()[0]
    print(f"raw.orders loaded -> {count} rows")

    # Load Customers
    print("Loading Customers....")
    customers = read_parquet_from_s3('raw/customers/customers.parquet')
    con.execute("DROP TABLE IF EXISTS raw.customers")
    con.execute("CREATE TABLE raw.customers AS SELECT * FROM customers")
    count = con.execute("SELECT COUNT(*) FROM raw.customers").fetchone()[0]
    print(f"raw.customers loaded -> {count} rows")

    # Load Payments
    print("Loading Payments....")
    payments = read_parquet_from_s3('raw/payments/payments.parquet')
    con.execute("DROP TABLE IF EXISTS raw.payments")
    con.execute("CREATE TABLE raw.payments AS SELECT * FROM payments")
    count = con.execute("SELECT COUNT(*) FROM raw.payments").fetchone()[0]
    print(f"raw.payments loaded -> {count} rows")

    # Load Products
    print("Loading Products....")
    products = read_parquet_from_s3('raw/products/products.parquet')
    con.execute("DROP TABLE IF EXISTS raw.products")
    con.execute("CREATE TABLE raw.products AS SELECT * FROM products")
    count = con.execute("SELECT COUNT(*) FROM raw.products").fetchone()[0]
    print(f"raw.products loaded -> {count} rows")

    #------Summary--------------------
    print("\nWarehouse Summary: ")
    tables = con.execute("""SELECT table_name, estimated_size 
                        FROM duckdb_tables 
                        WHERE schema_name = 'raw'""").fetchall()

    for table in tables:
        print(f" -> raw.{table[0]}")

    con.close()
    print("\nAll data loaded into warehouse successfully! ")

if __name__ == "__main__":
    load_to_warehouse()

