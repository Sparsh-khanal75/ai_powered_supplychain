import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

def generate_sales_forecast(sales_data: list[dict], months_ahead: int = 3):
    """
    sales_data = [
        {"month": "2025-01", "sales": 1200},
        {"month": "2025-02", "sales": 1350},
        {"month": "2025-03", "sales": 1280},
    ]
    """
    if not sales_data:
        return []

    # Convert to DataFrame
    df = pd.DataFrame(sales_data)
    df["t"] = np.arange(len(df))  # timeline index

    # Train simple linear regression model
    model = LinearRegression()
    model.fit(df[["t"]], df["sales"])

    # Predict next n months
    future_t = np.arange(len(df), len(df) + months_ahead).reshape(-1, 1)
    predictions = model.predict(future_t)

    # Build forecast output
    forecasts = []
    last_month = pd.to_datetime(df["month"].iloc[-1])

    for i in range(months_ahead):
        next_month = (last_month + pd.DateOffset(months=i + 1)).strftime("%Y-%m")
        forecasts.append({
            "month": next_month,
            "predicted_sales": float(predictions[i])
        })

    return forecasts
