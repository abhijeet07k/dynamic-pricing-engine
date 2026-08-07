import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# ============================================
# Configuration
# ============================================

API_URL = "https://dynamic-pricing-engine-5.onrender.com"

st.set_page_config(
    page_title="Dynamic Pricing Engine",
    page_icon="💰",
    layout="wide"
)

# ============================================
# Load Dataset
# ============================================

@st.cache_data
def load_data():
    df = pd.read_csv(
        "online_retail_II.csv",
        encoding="cp1252"
    )

    df["StockCode"] = df["StockCode"].astype(str)

    countries = sorted(
        df["Country"].dropna().unique().tolist()
    )

    products = (
        df[["StockCode", "Description"]]
        .drop_duplicates()
        .dropna()
        .sort_values("Description")
    )

    return countries, products

countries, products = load_data()

# ============================================
# API Helper
# ============================================

def call_api(endpoint, payload):

    try:

        response = requests.post(
            f"{API_URL}/{endpoint}",
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        return response.json(), None

    except requests.exceptions.Timeout:
        return None, "Request Timeout"

    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to FastAPI server."

    except requests.exceptions.HTTPError:
        return None, response.text

    except Exception as e:
        return None, str(e)

# ============================================
# Header
# ============================================

st.title("💰 Dynamic Pricing Engine")

st.markdown(
"""
AI-powered Dynamic Pricing Recommendation System
"""
)

# ============================================
# Sidebar
# ============================================

st.sidebar.header("Product Information")

product_display = [
    f"{row.StockCode} - {row.Description}"
    for _, row in products.iterrows()
]

selected_product = st.sidebar.selectbox(
    "Select Product",
    product_display
)

stock_code = selected_product.split(" - ")[0]

country = st.sidebar.selectbox(
    "Country",
    countries
)

current_price = st.sidebar.number_input(
    "Current Price",
    value=100.0,
    min_value=0.0
)

cost_price = st.sidebar.number_input(
    "Cost Price",
    value=70.0,
    min_value=0.0
)

competitor_price = st.sidebar.number_input(
    "Competitor Price",
    value=95.0,
    min_value=0.0
)

inventory = st.sidebar.number_input(
    "Inventory",
    value=150,
    min_value=0
)

month = st.sidebar.slider(
    "Month",
    1,
    12,
    12
)

hour = st.sidebar.slider(
    "Hour",
    0,
    23,
    18
)

holiday = st.sidebar.selectbox(
    "Holiday",
    [0,1]
)

weekend = st.sidebar.selectbox(
    "Weekend",
    [0,1]
)

# ============================================
# Predict Demand
# ============================================

st.subheader("Demand Prediction")

if st.button(
    "Predict Demand",
    use_container_width=True
):

    payload = {

        "Price": current_price,
        "CompetitorPrice": competitor_price,
        "Inventory": inventory,
        "Month": month,
        "Hour": hour,
        "Holiday": holiday,
        "Weekend": weekend,
        "StockCode": stock_code,
        "Country": country

    }

    with st.spinner("Predicting Demand..."):

        result, error = call_api(
            "predict-demand",
            payload
        )

    if error:

        st.error(error)

    else:

        st.success(
            f"Predicted Demand : {result['PredictedDemand']:.2f}"
        )

# ============================================
# Recommend Price
# ============================================

st.subheader("Price Recommendation")

if st.button(
    "Recommend Price",
    use_container_width=True
):

    payload = {

        "CurrentPrice": current_price,
        "CostPrice": cost_price,
        "CompetitorPrice": competitor_price,
        "Inventory": inventory,
        "Month": month,
        "Hour": hour,
        "Holiday": holiday,
        "Weekend": weekend,
        "StockCode": stock_code,
        "Country": country

    }

    with st.spinner("Optimizing Price..."):

        result, error = call_api(
            "recommend-price",
            payload
        )

    if error:

        st.error(error)

    else:

        st.success("Recommendation Generated")

        col1,col2,col3,col4 = st.columns(4)

        revenue = (
            result["RecommendedPrice"]
            * result["ExpectedDemand"]
        )

        col1.metric(
            "Recommended Price",
            f"₹{result['RecommendedPrice']:.2f}"
        )

        col2.metric(
            "Expected Demand",
            f"{result['ExpectedDemand']:.2f}"
        )

        col3.metric(
            "Expected Revenue",
            f"₹{revenue:.2f}"
        )

        col4.metric(
            "Expected Profit",
            f"₹{result['ExpectedProfit']:.2f}"
        )

        simulation = result.get("Simulation")

        if simulation:

            df = pd.DataFrame(simulation)

            st.divider()

            st.subheader("Simulation Analysis")

            fig = px.line(
                df,
                x="Price",
                y="Demand",
                markers=True,
                title="Price vs Demand"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            fig = px.line(
                df,
                x="Price",
                y="Revenue",
                markers=True,
                title="Price vs Revenue"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            fig = px.line(
                df,
                x="Price",
                y="Profit",
                markers=True,
                title="Price vs Profit"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.subheader("Simulation Table")

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.warning(
                "Simulation data not returned by API."
            )

# ============================================
# Footer
# ============================================

st.divider()

