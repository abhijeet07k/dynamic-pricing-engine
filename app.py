import streamlit as st
import requests
import pandas as pd
import plotly.express as px
#Page Configuration
st.set_page_config(
    page_title="Dynamic Pricing Engine",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Dynamic Pricing Engine")
st.write("AI-powered Dynamic Pricing Recommendation System")
#Sidebar Inputs
st.sidebar.header("Input Product Details")

stock_code = st.sidebar.text_input(
    "Product Code",
    "85123A"
)

country = st.sidebar.text_input(
    "Country",
    "United Kingdom"
)

current_price = st.sidebar.number_input(
    "Current Price",
    value=100.0
)

cost_price = st.sidebar.number_input(
    "Cost Price",
    value=70.0
)

competitor_price = st.sidebar.number_input(
    "Competitor Price",
    value=95.0
)

inventory = st.sidebar.number_input(
    "Inventory",
    value=150
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
#Predict Demand Button
if st.button("Predict Demand"):

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

    response = requests.post(
        "https://dynamic-pricing-engine-5.onrender.com/predict-demand",
        json=payload
    )

    if response.status_code == 200:

        demand = response.json()["PredictedDemand"]

        st.success(f"Predicted Demand: {demand:.2f}")

    else:

        st.error(response.text)
#Recommend Price Button
if st.button("Recommend Price"):

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

    response = requests.post(
        "https://dynamic-pricing-engine-5.onrender.com/recommend-price",
        json=payload
    )

    if response.status_code == 200:

        result = response.json()

        st.success("Recommendation Generated")

        c1,c2,c3,c4 = st.columns(4)

        c1.metric(
            "Recommended Price",
            f"₹{result['RecommendedPrice']:.2f}"
        )

        c2.metric(
            "Predicted Demand",
            result["ExpectedDemand"]
        )

        revenue = (
            result["RecommendedPrice"]
            *
            result["ExpectedDemand"]
        )

        c3.metric(
            "Expected Revenue",
            f"₹{revenue:.2f}"
        )

        c4.metric(
            "Expected Profit",
            f"₹{result['ExpectedProfit']:.2f}"
        )

        df = pd.DataFrame(
            result["Simulation"]
        )
#Price vs Demand
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
        #Price vs Revenue
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
        #Price vs Profit
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
        #Simulation Table
        st.subheader("Simulation Results")

st.dataframe(
    df,
    use_container_width=True
)
