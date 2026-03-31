import numpy as np
import pandas as pd

def calculate_elasticity(df):
    """
    Calculate Price Elasticity of Demand
    Formula: % change in quantity / % change in price
    """
    try:
        # Sort by price
        df = df.sort_values('price')

        # Calculate percentage changes
        price_change = df['price'].pct_change()
        quantity_change = df['units_sold'].pct_change()

        # Calculate elasticity
        elasticity = quantity_change / price_change

        # Remove infinite and NaN values
        elasticity = elasticity.replace([np.inf, -np.inf], np.nan).dropna()

        # Average elasticity
        avg_elasticity = round(elasticity.mean(), 2)

        # Interpret elasticity
        if avg_elasticity < -1:
            interpretation = "Price Sensitive — Lowering price will increase revenue"
        elif avg_elasticity == -1:
            interpretation = "Unit Elastic — Price change has no effect on revenue"
        else:
            interpretation = "Price Insensitive — You can raise price without losing many customers"

        # Build chart data
        chart_data = []
        for _, row in df.iterrows():
            chart_data.append({
                "price": row['price'],
                "units_sold": row['units_sold']
            })

        return {
            "elasticity": avg_elasticity,
            "interpretation": interpretation,
            "chart_data": chart_data
        }

    except Exception as e:
        return {"error": str(e)}