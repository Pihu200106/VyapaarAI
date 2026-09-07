import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from io import BytesIO
import base64
from sklearn.linear_model import LinearRegression
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
        top_products = (
            df.groupby('product')['quantity_sold']
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )
        insights['top_selling_products'] = top_products.to_dict()
    else:
        insights['top_selling_products'] = (
            "'product' or 'quantity_sold' column missing"
        )

    # Low Stock Alerts
    if {'stock_left', 'product'}.issubset(df.columns):
        low_stock = df[df['stock_left'] < 5]['product'].unique().tolist()
        insights['low_stock_alerts'] = low_stock
    else:
        insights['low_stock_alerts'] = "'stock_left' column missing"

    # Top 3 Frequent Customers
    if 'customer_id' in df.columns:
        frequent_customers = (
            df['customer_id']
            .value_counts()
            .head(3)
            .to_dict()
        )
        insights['frequent_customers'] = frequent_customers
    else:
        insights['frequent_customers'] = "'customer_id' column missing"

    # Monthly Sales Trend
    trend = extract_monthly_sales(df)

    if trend:
        insights['monthly_sales_trend'] = trend
    else:
        insights['monthly_sales_trend'] = (
            "'date' or 'quantity_sold' column missing"
        )

    # Revenue by Product
    if {'product', 'quantity_sold', 'unit_price'}.issubset(df.columns):
        df['revenue'] = df['quantity_sold'] * df['unit_price']

        revenue_data = (
            df.groupby('product')['revenue']
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )

        insights['top_revenue_products'] = (
            revenue_data.round(2).to_dict()
        )

    return insights


# ------------------------------
# SMART ADVICE
# ------------------------------
def generate_personalized_advice(insights):
    messages = []

    top = insights.get('top_selling_products', {})

    if isinstance(top, dict) and top:
        best = list(top.keys())[:2]

        messages.append(
            f"Focus on best-selling products like "
            f"{', '.join(best)}. Consider running promotions."
        )

    low = insights.get('low_stock_alerts', [])

    if isinstance(low, list) and low:
        messages.append(
            f"Reorder low stock items: "
            f"{', '.join(low)} to avoid stockouts."
        )

    loyal = insights.get('frequent_customers', {})

    if isinstance(loyal, dict) and loyal:
        top_loyals = list(loyal.keys())[:2]

        messages.append(
            f"Reward frequent customers like "
            f"{', '.join(top_loyals)} with loyalty offers."
        )

    rev = insights.get('top_revenue_products', {})

    if isinstance(rev, dict) and rev:
        best_rev = list(rev.keys())[0]

        messages.append(
            f"{best_rev} is generating the highest revenue. "
            f"Focus on maximizing its margins."
        )

    return (
        " ".join(messages)
        if messages
        else "Business appears stable. Keep up the good work!"
    )


# ------------------------------
# FORECASTING
# ------------------------------
def forecast_top_products(user_folder):
    warnings_imported = False

    try:
        import warnings
        warnings.filterwarnings("ignore")

        all_data = []

        # Get only CSV files
        files = sorted(
            [
                f for f in os.listdir(user_folder)
                if f.lower().endswith(".csv")
            ]
        )

        # Read all CSV files
        for file in files:
            path = os.path.join(user_folder, file)

            df = pd.read_csv(path)
            df = clean_dataframe(df)

            # Required columns
            required_columns = {
                'product',
                'quantity_sold',
                'date'
            }

            if not required_columns.issubset(df.columns):
                continue

            # Convert date
            df['date'] = pd.to_datetime(
                df['date'],
                errors='coerce'
            )

            # Convert quantity to numeric
            df['quantity_sold'] = pd.to_numeric(
                df['quantity_sold'],
                errors='coerce'
            )

            # Remove invalid rows
            df.dropna(
                subset=[
                    'date',
                    'quantity_sold',
                    'product'
                ],
                inplace=True
            )

            if not df.empty:
                all_data.append(
                    df[
                        [
                            'date',
                            'product',
                            'quantity_sold'
                        ]
                    ]
                )

        # No valid CSV data
        if not all_data:
            return {
                "error": "No valid sales data found."
            }

        # Combine all CSV files
        combined_df = pd.concat(
            all_data,
            ignore_index=True
        )

        # Convert dates to monthly periods
        combined_df['month'] = (
            combined_df['date']
            .dt.to_period('M')
        )

        # Calculate monthly sales per product
        monthly_sales = (
            combined_df
            .groupby(
                ['product', 'month']
            )['quantity_sold']
            .sum()
        )

        predictions = {}

        # Forecast each product
        for product in combined_df['product'].unique():

            try:
                # Get this product's monthly sales
                product_data = monthly_sales[
                    monthly_sales
                    .index
                    .get_level_values('product') == product
                ]

                # Need at least 3 months
                if len(product_data) < 3:
                    continue

                # Sort by month
                product_data = product_data.sort_index()

                sales_series = (
                    product_data
                    .values
                    .astype(float)
                )

                # Linear Regression for next-month sales forecasting
                X = np.arange(len(sales_series)).reshape(-1, 1)
                y = sales_series
                model = LinearRegression()
                model.fit(X, y)

                # Forecast next month
                next_month_index = np.array([[len(sales_series)]])
                forecast = model.predict(next_month_index)[0]

                # Prevent negative forecast
                forecast = max(0, forecast)

                predictions[product] = round(
                    forecast
                )

            except Exception:
                continue

        # No product has enough historical data
        if not predictions:
            return {
                "message":
                "Not enough monthly historical data for forecasting."
            }

        # Get top 3 predicted products
        top3 = dict(
            sorted(
                predictions.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
        )

        return top3

    except Exception as e:
        return {
            "error": str(e)
        }


# ------------------------------
# PLOTTING UTILITIES
# ------------------------------
def _plot_to_base64():
    buf = BytesIO()

    plt.savefig(
        buf,
        format="png",
        bbox_inches="tight"
    )

    buf.seek(0)

    return (
        "data:image/png;base64,"
        + base64.b64encode(
            buf.read()
        ).decode()
    )


# ------------------------------
# MONTHLY SALES
# ------------------------------
def extract_monthly_sales(df):
    try:
        df = clean_dataframe(df)

        date_col = next(
            (
                col
                for col in df.columns
                if 'date' in col.lower()
            ),
            None
        )

        if (
            not date_col
            or 'quantity_sold' not in df.columns
        ):
            return None

        df[date_col] = pd.to_datetime(
            df[date_col],
            errors='coerce'
        )

        df['quantity_sold'] = pd.to_numeric(
            df['quantity_sold'],
            errors='coerce'
        )

        df.dropna(
            subset=[
                date_col,
                'quantity_sold'
            ],
            inplace=True
        )

        df['month'] = (
            df[date_col]
            .dt.to_period("M")
            .astype(str)
        )

        trend = (
            df.groupby('month')['quantity_sold']
            .sum()
            .astype(int)
        )

        return trend.to_dict()

    except Exception:
        return None


# ------------------------------
# SALES CHART
# ------------------------------
def generate_sales_plot(df):
    try:
        df = clean_dataframe(df)

        date_col = next(
            (
                col
                for col in df.columns
                if 'date' in col.lower()
            ),
            None
        )

        if (
            not date_col
            or 'quantity_sold' not in df.columns
        ):
            return None

        df[date_col] = pd.to_datetime(
            df[date_col],
            errors='coerce'
        )

        df['quantity_sold'] = pd.to_numeric(
            df['quantity_sold'],
            errors='coerce'
        )

        df.dropna(
            subset=[
                date_col,
                'quantity_sold'
            ],
            inplace=True
        )

        df['month'] = (
            df[date_col]
            .dt.to_period("M")
            .astype(str)
        )

        trend = (
            df.groupby('month')['quantity_sold']
            .sum()
            .reset_index()
        )

        plt.figure(figsize=(8, 4))

        sns.lineplot(
            data=trend,
            x='month',
            y='quantity_sold',
            marker='o'
        )

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


# ------------------------------
# TOP PRODUCT PIE CHART
# ------------------------------
def generate_top_product_pie(df):
    try:
        df = clean_dataframe(df)

        if {
            'product',
            'quantity_sold'
        }.issubset(df.columns):

            top = (
                df.groupby('product')['quantity_sold']
                .sum()
                .sort_values(ascending=False)
                .head(5)
            )

            plt.figure(figsize=(6, 6))

            top.plot.pie(
                autopct='%1.1f%%',
                startangle=90,
                label=''
            )

            plt.title(
                "Top 5 Products by Quantity Sold"
            )

            plt.ylabel("")

            img = _plot_to_base64()

            plt.close()

            return img

    except Exception:
        return None


# ------------------------------
# TOP CUSTOMERS CHART
# ------------------------------
def generate_top_customers_plot(df):
    try:
        df = clean_dataframe(df)

        if 'customer_id' in df.columns:

            top = (
                df['customer_id']
                .value_counts()
                .head(5)
            )

            plt.figure(figsize=(6, 4))

            sns.barplot(
                x=top.index,
                y=top.values,
                palette="magma"
            )

            plt.title(
                "Top 5 Customers by Purchase Frequency"
            )

            plt.xlabel("Customer ID")
            plt.ylabel("Number of Purchases")

            img = _plot_to_base64()

            plt.close()

            return img

    except Exception:
        return None