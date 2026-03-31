import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def calculate_optimal_price(df):
    """
    Find the optimal price that maximizes revenue
    using Linear Regression
    """
    try:
        # Prepare data
        X = df['price'].values.reshape(-1, 1)
        y = df['units_sold'].values

        # Train linear regression model
        model = LinearRegression()
        model.fit(X, y)

        # Generate price range to test
        min_price = df['price'].min()
        max_price = df['price'].max()
        price_range = np.linspace(min_price, max_price, 100)

        # Predict units sold for each price
        predicted_units = model.predict(price_range.reshape(-1, 1))

        # Calculate revenue for each price
        revenues = price_range * predicted_units

        # Find price that gives maximum revenue
        optimal_index = np.argmax(revenues)
        optimal_price = round(price_range[optimal_index], 2)
        optimal_revenue = round(revenues[optimal_index], 2)

        # Current average price and revenue
        current_price = round(df['price'].mean(), 2)
        current_revenue = round((df['price'] * df['units_sold']).mean(), 2)

        # Build chart data
        chart_data = []
        for price, revenue in zip(price_range, revenues):
            chart_data.append({
                "price": round(price, 2),
                "revenue": round(revenue, 2)
            })

        return {
            "optimal_price": optimal_price,
            "optimal_revenue": optimal_revenue,
            "current_price": current_price,
            "current_revenue": current_revenue,
            "revenue_increase": round(optimal_revenue - current_revenue, 2),
            "chart_data": chart_data
        }

    except Exception as e:
        return {"error": str(e)}