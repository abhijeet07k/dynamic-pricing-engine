from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib
import os

app = FastAPI(
    title="Dynamic Pricing Engine",
    version="1.0"
)

BASE_DIR = os.path.dirname(__file__)

model = joblib.load(os.path.join(BASE_DIR, "model.pkl"))
le_product = joblib.load(os.path.join(BASE_DIR, "le_product.pkl"))
le_country = joblib.load(os.path.join(BASE_DIR, "le_country.pkl"))
class Product(BaseModel):
    Price: float
    CompetitorPrice: float
    Inventory: int
    Month: int
    Hour: int
    Holiday: int
    Weekend: int
    StockCode: str
    Country: str


@app.post("/predict-demand")
def predict_demand(data: Product):

    product = le_product.transform([data.StockCode])[0]
    country = le_country.transform([data.Country])[0]

    sample = pd.DataFrame({
        "Price": [data.Price],
        "CompetitorPrice": [data.CompetitorPrice],
        "Inventory": [data.Inventory],
        "Month": [data.Month],
        "Hour": [data.Hour],
        "Holiday": [data.Holiday],
        "Weekend": [data.Weekend],
        "StockCode": [product],
        "Country": [country]
    })

    prediction = model.predict(sample)[0]

    return {
        "PredictedDemand": round(float(prediction), 2)
    }


# -----------------------------
# Second request model
# -----------------------------
class PricingRequest(BaseModel):
    CurrentPrice: float
    CostPrice: float
    CompetitorPrice: float
    Inventory: int
    Month: int
    Hour: int
    Holiday: int
    Weekend: int
    StockCode: str
    Country: str


@app.post("/recommend-price")
def recommend_price(data: PricingRequest):

    candidate_prices = np.arange(
        data.CurrentPrice * 0.8,
        data.CurrentPrice * 1.21,
        5
    )

    best_price = None
    best_profit = -1
    best_quantity = 0
    simulations = []

    for price in candidate_prices:

        sample = pd.DataFrame({
            "Price": [price],
            "CompetitorPrice": [data.CompetitorPrice],
            "Inventory": [data.Inventory],
            "Month": [data.Month],
            "Hour": [data.Hour],
            "Holiday": [data.Holiday],
            "Weekend": [data.Weekend],
            "StockCode": [
                le_product.transform([data.StockCode])[0]
            ],
            "Country": [
                le_country.transform([data.Country])[0]
            ]
        })

        quantity = model.predict(sample)[0]
        quantity = max(0, quantity)

        revenue = price * quantity
        profit = (price - data.CostPrice) * quantity

        simulations.append({
            "Price": round(price, 2),
            "Demand": round(float(quantity), 2),
            "Revenue": round(float(revenue), 2),
            "Profit": round(float(profit), 2)
        })

        if profit > best_profit:
            best_profit = profit
            best_price = price
            best_quantity = quantity

    return {
        "RecommendedPrice": round(best_price, 2),
        "ExpectedDemand": round(float(best_quantity), 2),
        "ExpectedProfit": round(float(best_profit), 2),
        "Simulation": simulations
    }