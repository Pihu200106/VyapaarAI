import pandas as pd
import re

def clean_column_names(cols):
    return [re.sub(r'[^a-z0-9]', '_', col.strip().lower()) for col in cols]

def map_columns(df):
    col_map = {}

    for col in df.columns:
        name = col.lower()

        if any(key in name for key in ['product', 'item', 'sku']):
            col_map['product'] = col
        elif any(key in name for key in ['quantity', 'qty', 'sold', 'units']):
            col_map['quantity_sold'] = col
        elif any(key in name for key in ['stock', 'left', 'remaining']):
            col_map['stock_left'] = col
        elif any(key in name for key in ['customer', 'buyer', 'client', 'id']):
            col_map['customer_id'] = col
        elif any(key in name for key in ['date', 'order date', 'created']):
            col_map['date'] = col

    return col_map

# Clean & Standardize DataFrame
def clean_dataframe(df):
    df.columns = clean_column_names(df.columns)
    col_map = map_columns(df)

    required_keys = ['product', 'quantity_sold', 'stock_left', 'customer_id']
    missing = [k for k in required_keys if k not in col_map]
    if missing:
        raise ValueError(f"Missing important fields: {missing}")

    # Rename columns to standard ones
    df = df.rename(columns={v: k for k, v in col_map.items()})

    # Fill missing values
    df['quantity_sold'] = pd.to_numeric(df['quantity_sold'], errors='coerce').fillna(0).astype(int)
    df['stock_left'] = pd.to_numeric(df['stock_left'], errors='coerce').fillna(0).astype(int)
    df['product'] = df['product'].astype(str).str.strip()
    df['customer_id'] = df['customer_id'].astype(str).str.strip()

    # Handle dates (optional)
    if 'date' in col_map:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

    return df
