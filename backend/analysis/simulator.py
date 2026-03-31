import pandas as pd
import numpy as np

def simulate_discount(df, discount_pct, elasticity):
    """
    Simulate the impact of a discount on revenue
    """
    try:
        # Current values
        current_price = df['price'].mean()
        current_units = df['units_sold'].mean()
        current_revenue = current_price * current_units

        # New price after discount
        new_price = current_price * (1 - discount_pct / 100)

        # Price change percentage
        price_change_pct = (new_price - current_price) / current_price

        # New units sold based on elasticity
        new_units = current_units * (1 + elasticity * price_change_pct)

        # New revenue
        new_revenue = new_price * new_units

        # Revenue change
        revenue_change = round(new_revenue - current_revenue, 2)
        revenue_change_pct = round((revenue_change / current_revenue) * 100, 2)

        return {
            "current_price": round(current_price, 2),
            "new_price": round(new_price, 2),
            "current_revenue": round(current_revenue, 2),
            "new_revenue": round(new_revenue, 2),
            "revenue_change": revenue_change,
            "revenue_change_pct": revenue_change_pct,
            "interpretation": "Revenue will increase" if revenue_change > 0 else "Revenue will decrease"
        }

    except Exception as e:
        return {"error": str(e)}


def simulate_bundling(df, bundle_discount_pct):
    """
    Simulate the impact of bundling two products together
    """
    try:
        # Average price of single product
        single_price = df['price'].mean()

        # Bundle price (two products with discount)
        bundle_price = (single_price * 2) * (1 - bundle_discount_pct / 100)

        # Current revenue per transaction
        current_revenue = single_price * df['units_sold'].mean()

        # Estimated bundle revenue (assume 20% more units with bundling)
        bundle_units = df['units_sold'].mean() * 1.2
        bundle_revenue = bundle_price * bundle_units

        # Revenue change
        revenue_change = round(bundle_revenue - current_revenue, 2)
        revenue_change_pct = round((revenue_change / current_revenue) * 100, 2)

        return {
            "single_price": round(single_price, 2),
            "bundle_price": round(bundle_price, 2),
            "current_revenue": round(current_revenue, 2),
            "bundle_revenue": round(bundle_revenue, 2),
            "revenue_change": revenue_change,
            "revenue_change_pct": revenue_change_pct,
            "interpretation": "Bundling will increase revenue" if revenue_change > 0 else "Bundling will decrease revenue"
        }

    except Exception as e:
        return {"error": str(e)}