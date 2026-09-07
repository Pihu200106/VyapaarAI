import streamlit as st
import pandas as pd
import json
import os
import datetime
import requests

from biz_insights import (
    generate_insights,
    generate_personalized_advice,
    forecast_top_products,
    generate_sales_plot,
    generate_top_product_pie,
    generate_top_customers_plot
)
from data_cleaner import clean_dataframe

# ------------------------------
# Config
# ------------------------------
TWILIO_API_URL = "http://localhost:5000/send-whatsapp"
USER_DB = "users.json"

# ------------------------------
# Load or Initialize User Data
# ------------------------------
if not os.path.exists(USER_DB):
    with open(USER_DB, "w") as f:
        json.dump({}, f)

with open(USER_DB, "r") as f:
    users = json.load(f)

# ------------------------------
# App Title
# ------------------------------
st.set_page_config(page_title="VyapaarAI V2", layout="centered")
st.title("VyapaarAI – Smart Assistant for Small Businesses")

# ------------------------------
# Sidebar Info & Logout
# ------------------------------
if 'user_phone' in st.session_state:
    st.sidebar.success(f"Logged in as: {st.session_state.user_phone}")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

# ------------------------------
# User Registration
# ------------------------------
if 'user_phone' not in st.session_state:
    st.header("Register Your Business")
    with st.form("register_form"):
        name = st.text_input("Business Owner Name")
        phone = st.text_input("WhatsApp Number (+91XXXXXXXXXX)")
        submitted = st.form_submit_button("Register")

    if submitted:
        name = name.strip()
        phone = phone.strip().replace(" ", "")
        if name and phone.startswith("+91") and len(phone) == 13 and phone[1:].isdigit():
            users[phone] = {"name": name}
            with open(USER_DB, "w") as f:
                json.dump(users, f, indent=2)
            st.session_state.user_phone = phone
            st.success(f"Registered {name} ({phone}) successfully.")
            st.rerun()
        else:
            st.error("Invalid WhatsApp number. Format: +91XXXXXXXXXX")

# ------------------------------
# Upload + Analysis
# ------------------------------
if 'user_phone' in st.session_state:
    st.header("Upload Monthly Sales CSV")

    uploaded_file = st.file_uploader("Upload your sales .csv file", type=["csv"])
    phone = st.session_state.user_phone
    folder_path = os.path.join("data", phone)
    os.makedirs(folder_path, exist_ok=True)

    if uploaded_file and not st.session_state.get("upload_handled"):
        try:
            raw_df = pd.read_csv(uploaded_file)
            df = clean_dataframe(raw_df)

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{timestamp}.csv"
            save_path = os.path.join(folder_path, filename)
            df.to_csv(save_path, index=False)

            st.success(f"Uploaded and saved as `{filename}`")
            st.session_state.upload_handled = True
            st.rerun()

        except Exception as e:
            st.error("Failed to process the uploaded file.")
            st.code(str(e))

    # ------------------------------
    # Show Insights from All Files
    # ------------------------------
    st.header("Past Uploads – Smart Insights")
    all_files = sorted(os.listdir(folder_path))

    if all_files:
        for file in all_files:
            with st.expander(f"{file}"):
                try:
                    df = pd.read_csv(os.path.join(folder_path, file))
                    df = clean_dataframe(df)

                    insights = generate_insights(df)
                    suggestion = generate_personalized_advice(insights)

                    st.subheader("Key Insights")
                    st.json(insights)

                    st.subheader("Personalized Suggestions")
                    st.success(suggestion)

                    # Visual Trends
                    st.markdown("### Visual Trends")
                    sales_plot = generate_sales_plot(df)
                    pie_chart = generate_top_product_pie(df)
                    top_customers = generate_top_customers_plot(df)

                    if sales_plot:
                        st.image(sales_plot, caption="Monthly Sales Trend")
                    if pie_chart:
                        st.image(pie_chart, caption="Top 5 Products (Sales %)")
                    if top_customers:
                        st.image(top_customers, caption="Top 5 Customers")

                    # WhatsApp Button
                    if st.button(f"Send summary on WhatsApp", key=file):
                        try:
                            res = requests.post(
                                TWILIO_API_URL,
                                json={"phone": phone, "message": f"Summary for {file}:\n{suggestion}"}
                            )
                            if res.status_code == 200:
                                st.success("Summary sent via WhatsApp.")
                            else:
                                st.error("Failed to send the summary.")
                        except Exception as e:
                            st.warning("WhatsApp API error")
                            st.code(str(e))
                except Exception as e:
                    st.error(f"Could not read or analyze: {file}")
                    st.code(str(e))
    else:
        st.info("No past uploads found.")

    # ------------------------------
    # Forecasting (3+ files)
    # ------------------------------
    st.header("Sales Forecast for Next Month")
    if len(all_files) >= 3:
        forecast = forecast_top_products(folder_path)
        if "error" in forecast:
            st.warning(f"Forecasting failed: {forecast['error']}")
        elif forecast:
            st.success("Predicted Top Products:")
            st.json(forecast)
        else:
            st.info("No clear trend found for forecasting.")
    else:
        st.info("Upload at least 3 months of data to enable forecasting.")

else:
    st.info("Please register to get started.")
