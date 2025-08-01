import streamlit as st
import pandas as pd
from biz_insights import generate_insights, generate_gpt_advice
import matplotlib.pyplot as plt

# --------------------
# Page Setup
# --------------------
st.set_page_config(page_title="VyapaarAI", layout="centered")
st.title("VyapaarAI – Smart Assistant for Small Businesses")
st.markdown("Upload your sales CSV to get personalized business insights that grow with your business.")

# --------------------
# Upload CSV
# --------------------
uploaded_file = st.file_uploader("Upload your sales data (.csv)", type=["csv"])
st.markdown("""
**Required Columns in CSV:**

- `product`: Name of the product sold  
- `quantity_sold`: How many units sold  
- `stock_left`: Remaining stock after sales  
- `customer_id`: Unique customer identifier  
""")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        # Validate required columns
        required_cols = {'product', 'quantity_sold', 'stock_left', 'customer_id'}
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            st.error(f"Missing required columns: {', '.join(missing)}")
            st.stop()

        # File & Preview
        st.success("File uploaded successfully!")
        st.write("### Preview of your data:")
        st.dataframe(df.head())

        # --------------------
        # Insights
        # --------------------
        insights = generate_insights(df)

        # Top Selling Products (Bar Chart)
        st.write("### Top Selling Products")
        top_df = pd.Series(insights['top_selling_products']).sort_values(ascending=True)
        fig1, ax1 = plt.subplots()
        top_df.plot(kind='barh', color='skyblue', ax=ax1)
        ax1.set_xlabel("Quantity Sold")
        ax1.set_title("Top Products")
        st.pyplot(fig1)

        # Low Stock (Pie or List)
        st.write("### Low Stock Alerts")
        low_stock = insights['low_stock_alerts']
        if low_stock:
            fig2, ax2 = plt.subplots()
            low_stock_counts = df[df['product'].isin(low_stock)]['product'].value_counts()
            ax2.pie(low_stock_counts, labels=low_stock_counts.index, autopct='%1.1f%%', startangle=140)
            ax2.axis('equal')
            st.pyplot(fig2)
        else:
            st.success("All products have sufficient stock.")

        # Frequent Customers
        st.write("### Frequent Customers")
        st.json(insights['frequent_customers'])

        # --------------------
        # GPT Suggestions (if enabled)
        # --------------------
        st.write("### Smart Suggestions")
        try:
            suggestion = generate_gpt_advice(insights)
            st.success(suggestion)
        except Exception as e:
            st.warning("Smart suggestions are currently unavailable. Enable billing to use GPT-based insights.")
            st.caption(f"(Debug info: {e})")

    except Exception as e:
        st.error("Failed to process the file. Make sure it's a valid CSV.")
        st.code(str(e))
else:
    st.info("Please upload a CSV file to begin.")
