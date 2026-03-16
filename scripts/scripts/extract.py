import pandas as pd
import boto3
import io

BUCKET_NAME = 'de-project-olist-data'  # ← your bucket name
DATA_PATH   = '/home/ubuntu/de-project/data'


def upload_to_s3(df, s3_key):
    """Convert DataFrame to Parquet and upload to S3"""
    s3     = boto3.client('s3')
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    s3.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=buffer.getvalue())
    print(f"✅ Uploaded {len(df)} rows → s3://{BUCKET_NAME}/{s3_key}")


def read_csv_chunked(filepath, chunksize=10000):
    """Read large CSV in chunks to save RAM"""
    chunks = []
    for chunk in pd.read_csv(filepath, chunksize=chunksize):
        chunks.append(chunk)
    return pd.concat(chunks, ignore_index=True)


def extract_orders():
    print("  Loading orders...")
    df = read_csv_chunked(f'{DATA_PATH}/olist_orders_dataset.csv')

    df.drop_duplicates(subset='order_id', inplace=True)
    df.dropna(subset=['order_id', 'customer_id'], inplace=True)

    for col in ['order_purchase_timestamp',
                'order_approved_at',
                'order_delivered_customer_date',
                'order_estimated_delivery_date']:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    upload_to_s3(df, 'raw/orders/orders.parquet')
    return len(df)


def extract_customers():
    print("  Loading customers...")
    df = read_csv_chunked(f'{DATA_PATH}/olist_customers_dataset.csv')

    df.drop_duplicates(subset='customer_id', inplace=True)
    df.dropna(subset=['customer_id'], inplace=True)

    upload_to_s3(df, 'raw/customers/customers.parquet')
    return len(df)


def extract_payments():
    print("  Loading payments...")
    df = read_csv_chunked(f'{DATA_PATH}/olist_order_payments_dataset.csv')

    df.drop_duplicates(inplace=True)
    df.dropna(subset=['order_id'], inplace=True)
    df = df[df['payment_value'] > 0]

    upload_to_s3(df, 'raw/payments/payments.parquet')
    return len(df)


def extract_products():
    print("  Loading products...")
    df = read_csv_chunked(f'{DATA_PATH}/olist_products_dataset.csv')

    df.drop_duplicates(subset='product_id', inplace=True)
    df.dropna(subset=['product_id'], inplace=True)

    upload_to_s3(df, 'raw/products/products.parquet')
    return len(df)


def run_extraction():
    print("🚀 Starting extraction...")
    print(f"  Orders    : {extract_orders()} rows")
    print(f"  Customers : {extract_customers()} rows")
    print(f"  Payments  : {extract_payments()} rows")
    print(f"  Products  : {extract_products()} rows")
    print("✅ Extraction complete!")


if __name__ == '__main__':
    run_extraction()