import pandas as pd

def compare_competitors(df):
    """
    Compare your prices with competitor prices
    """
    try:
        # Your average price
        your_avg_price = round(df['price'].mean(), 2)

        # Competitor average price
        competitor_avg_price = round(df['competitor_price'].mean(), 2)

        # Price difference
        price_difference = round(your_avg_price - competitor_avg_price, 2)

        # Percentage difference
        price_difference_pct = round(
            ((your_avg_price - competitor_avg_price) / competitor_avg_price) * 100, 2
        )

        # Interpretation
        if price_difference > 0:
            interpretation = f"You are pricing {abs(price_difference_pct)}% HIGHER than competitors"
            suggestion = "Consider lowering price or adding more value to justify higher price"
        elif price_difference < 0:
            interpretation = f"You are pricing {abs(price_difference_pct)}% LOWER than competitors"
            suggestion = "You have room to increase price and still stay competitive"
        else:
            interpretation = "Your price matches the competitor average"
            suggestion = "You are perfectly positioned in the market"

        # Build chart data
        chart_data = []
        for _, row in df.iterrows():
            chart_data.append({
                "date": str(row.get('date', '')),
                "your_price": row['price'],
                "competitor_price": row['competitor_price']
            })

        return {
            "your_avg_price": your_avg_price,
            "competitor_avg_price": competitor_avg_price,
            "price_difference": price_difference,
            "price_difference_pct": price_difference_pct,
            "interpretation": interpretation,
            "suggestion": suggestion,
            "chart_data": chart_data
        }

    except Exception as e:
        return {"error": str(e)}