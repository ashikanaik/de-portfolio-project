import os

import pandas as pd
import boto3
import io
from datetime import datetime, timedelta

#------------config------------------
BUCKET_NAME = 'de-project-olist-data'
#------------------------------------

def read_parquet_from_s3(s3_key):
    """Read a Parquet file from S3 into a DataFrame"""
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=BUCKET_NAME, Key=s3_key)
    buffer = io.BytesIO(response['Body'].read())
    return pd.read_parquet(buffer)

def check_nulls(df, columns, table_name):
    """Check that required columns have no nulls"""
    for col in columns:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            raise ValueError(f"NULL CHECK FAILED: {table_name}.{col} has {null_count} null values!")
        print(f"NULL CHECK PASSED -> {table_name}")

def check_uniqueness(df, columns, table_name):
    """Check that a column has no duplicate values"""
    duplicate_count = df[columns].duplicated().sum()
    if duplicate_count > 0:
        raise ValueError(f"UNIQUENESS CHECK FAILED: {table_name}.{columns} has {duplicate_count} duplicate values!")
    print(f"UNIQUENESS CHECK PASSED -> {table_name}")

def check_row_count(df, min_rows, table_name):
    """Check that a table has minimum expected rows"""
    if len(df) < min_rows:
        raise ValueError(f"ROW COUNT CHECK FAILED: {table_name} has {len(df)} rows, expected at least {min_rows} rows!")
    print(f"ROW COUNT CHECK PASSED -> {table_name} ({len(df)} rows)")

def check_positive_values(df, column, table_name):
    """Check that a numeric column has only positive values"""
    invalid = (df[column]<0).sum()
    if invalid > 0:
        raise ValueError(f"VALUE CHECK FAILED: {table_name}.{column} has {invalid} Non-Positive values!")
    print(f"VALUE CHECK PASSED -> {table_name}.{column}")

def run_quality_checks():
    print("Running quality checks...")

    #-------ORDERS-------------
    orders = read_parquet_from_s3('raw/orders/orders.parquet')
    check_nulls(orders,['order_id','customer_id'],'orders')
    check_uniqueness(orders,'order_id','orders')
    check_row_count(orders,50000,'orders')

    #-------CUSTOMERS----------
    customers = read_parquet_from_s3('raw/customers/customers.parquet')
    check_nulls(customers,['customer_id'],'customers')
    check_uniqueness(customers,'customer_id','customers')
    check_row_count(customers,50000,'customers')

    #-------PAYMENTS-------------
    payments = read_parquet_from_s3('raw/payments/payments.parquet')
    check_nulls(payments,['order_id'],'payments')
    check_positive_values(payments,'payment_value','payments')
    check_row_count(payments,50000,'payments')

    #-------PRODUCTS--------------
    products = read_parquet_from_s3('raw/products/products.parquet')
    check_nulls(products,['product_id'],'products')
    check_uniqueness(products,'product_id','products')
    check_row_count(products,10000,'products')

    print("\nAll quality checks passed! Pipeline can continue.")

if __name__ == "__main__":
    run_quality_checks()

