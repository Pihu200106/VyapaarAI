import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from io import BytesIO
import base64
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from data_cleaner import clean_dataframe

sns.set(style="whitegrid")

# ------------------------------
# SMART BUSINESS INSIGHTS
# ------------------------------
def generate_insights(df: pd.DataFrame):
    df = clean_dataframe(df)
    insights = {}

    # Top 5 Products by Quantity Sold
    if {'product', 'quantity_sold'}.issubset(df.columns):
        top_products = df.groupby('product')['quantity_sold'].sum().sort_values(ascending=False).head(5)
        insights['top_selling_products'] = top_products.to_dict()
    else:
        insights['top_selling_products'] = "'product' or 'quantity_sold' column missing"

    # Low Stock Alerts
    if {'stock_left', 'product'}.issubset(df.columns):
        low_stock = df[df['stock_left'] < 5]['product'].unique().tolist()
        insights['low_stock_alerts'] = low_stock
    else:
        insights['low_stock_alerts'] = "'stock_left' column missing"

    # Top 3 Frequent Customers
    if 'customer_id' in df.columns:
        frequent_customers = df['customer_id'].value_counts().head(3).to_dict()
        insights['frequent_customers'] = frequent_customers
    else:
        insights['frequent_customers'] = "'customer_id' column missing"

    # Monthly Sales Trend
    trend = extract_monthly_sales(df)
    insights['monthly_sales_trend'] = trend if trend else "'date' or 'quantity_sold' column missing"

    # Revenue by Product
    if {'product', 'quantity_sold', 'unit_price'}.issubset(df.columns):
        df['revenue'] = df['quantity_sold'] * df['unit_price']
        revenue_data = df.groupby('product')['revenue'].sum().sort_values(ascending=False).head(5)
        insights['top_revenue_products'] = revenue_data.round(2).to_dict()

    return insights

# ------------------------------
# SMART ADVICE
# ------------------------------
def generate_personalized_advice(insights):
    messages = []

    top = insights.get('top_selling_products', {})
    if isinstance(top, dict) and top:
        best = list(top.keys())[:2]
        messages.append(f"Focus on best-selling products like {', '.join(best)}. Consider running promotions.")

    low = insights.get('low_stock_alerts', [])
    if isinstance(low, list) and low:
        messages.append(f"Reorder low stock items: {', '.join(low)} to avoid stockouts.")

    loyal = insights.get('frequent_customers', {})
    if isinstance(loyal, dict) and loyal:
        top_loyals = list(loyal.keys())[:2]
        messages.append(f"Reward frequent customers like {', '.join(top_loyals)} with loyalty offers.")

    rev = insights.get('top_revenue_products', {})
    if isinstance(rev, dict) and rev:
        best_rev = list(rev.keys())[0]
        messages.append(f"{best_rev} is generating the highest revenue. Focus on maximizing its margins.")

    return " ".join(messages) if messages else "Business appears stable. Keep up the good work!"

# ------------------------------
# FORECASTING (CORRECTED)
# ------------------------------
def forecast_top_products(user_folder):
    from collections import defaultdict
    from statsmodels.tsa.holtwinters import SimpleExpSmoothing
    import warnings
    warnings.filterwarnings("ignore")

    try:
        product_monthly_sales = defaultdict(list)

        # Step 1: Sort files (so Jan, Feb, Mar stay in order)
        files = sorted(os.listdir(user_folder))

        for file in files:
            path = os.path.join(user_folder, file)
            df = pd.read_csv(path)
            df = clean_dataframe(df)

            # Detect relevant columns
            product_col = next((col for col in df.columns if 'product' in col.lower()), None)
            quantity_col = next((col for col in df.columns if 'quantity' in col.lower()), None)

            if not product_col or not quantity_col:
                continue

            df = df.rename(columns={product_col: "product", quantity_col: "quantity_sold"})

            # Summarize quantity sold per product in this file (1 month)
            month_sales = df.groupby("product")["quantity_sold"].sum().to_dict()

            for product in month_sales:
                product_monthly_sales[product].append(month_sales[product])

        # Step 2: Apply forecast only if we have 3+ months for a product
        predictions = {}
        for product, sales_series in product_monthly_sales.items():
            if len(sales_series) >= 3:
                model = SimpleExpSmoothing(sales_series).fit()
                next_month = model.forecast(1)[0]
                predictions[product] = round(next_month)

        # Step 3: Return top 3 forecasted
        top3 = dict(sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:3])
        return top3

    except Exception as e:
        return {"error": str(e)}

# ------------------------------
# PLOTTING UTILITIES
# ------------------------------
def _plot_to_base64():
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight')
    buf.seek(0)
    return f"data:image/png;base64,{base64.b64encode(buf.read()).decode()}"

def extract_monthly_sales(df):
    try:
        df = clean_dataframe(df)
        date_col = next((col for col in df.columns if 'date' in col.lower()), None)
        if not date_col or 'quantity_sold' not in df.columns:
            return None

        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df.dropna(subset=[date_col, 'quantity_sold'], inplace=True)
        df['month'] = df[date_col].dt.to_period("M").astype(str)
        trend = df.groupby('month')['quantity_sold'].sum().astype(int)
        return trend.to_dict()
    except:
        return None

# ------------------------------
# CHARTS
# ------------------------------
def generate_sales_plot(df):
    try:
        df = clean_dataframe(df)
        date_col = next((col for col in df.columns if 'date' in col.lower()), None)
        if not date_col or 'quantity_sold' not in df.columns:
            return None

        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df.dropna(subset=[date_col, 'quantity_sold'], inplace=True)
        df['month'] = df[date_col].dt.to_period("M").astype(str)
        trend = df.groupby('month')['quantity_sold'].sum().reset_index()

        plt.figure(figsize=(8, 4))
        sns.lineplot(data=trend, x='month', y='quantity_sold', marker='o')
        plt.title("Monthly Sales Trend")
        plt.xlabel("Month")
        plt.ylabel("Quantity Sold")
        plt.xticks(rotation=45)
        plt.tight_layout()

        img = _plot_to_base64()
        plt.close()
        return img
    except Exception as e:
        print("Plotting Error:", e)
        return None

def generate_top_product_pie(df):
    try:
        df = clean_dataframe(df)
        if {'product', 'quantity_sold'}.issubset(df.columns):
            top = df.groupby('product')['quantity_sold'].sum().sort_values(ascending=False).head(5)
            plt.figure(figsize=(6, 6))
            top.plot.pie(autopct='%1.1f%%', startangle=90, label='')
            plt.title("Top 5 Products by Quantity Sold")
            plt.ylabel("")
            img = _plot_to_base64()
            plt.close()
            return img
    except:
        return None

def generate_top_customers_plot(df):
    try:
        df = clean_dataframe(df)
        if 'customer_id' in df.columns:
            top = df['customer_id'].value_counts().head(5)
            plt.figure(figsize=(6, 4))
            sns.barplot(x=top.index, y=top.values, palette="magma")
            plt.title("Top 5 Customers by Purchase Frequency")
            plt.xlabel("Customer ID")
            plt.ylabel("Number of Purchases")
            img = _plot_to_base64()
            plt.close()
            return img
    except:
        return None
