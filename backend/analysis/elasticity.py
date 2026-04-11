import numpy as np


def calculate_elasticity(df):
    """
    Calculate Price Elasticity of Demand
    Formula: % change in quantity / % change in price
    """
    try:
        df = df.sort_values('price')

        price_change = df['price'].pct_change()
        quantity_change = df['units_sold'].pct_change()

        elasticity = quantity_change / price_change
        elasticity = elasticity.replace([np.inf, -np.inf], np.nan).dropna()

        avg_elasticity = round(elasticity.mean(), 2)

        if avg_elasticity < -1:
            interpretation = 'Price sensitive - lowering price is likely to increase revenue'
        elif avg_elasticity == -1:
            interpretation = 'Unit elastic - price changes are likely to keep revenue flat'
        else:
            interpretation = 'Price insensitive - there may be room to raise price with limited volume loss'

        chart_data = []
        for _, row in df.iterrows():
            chart_data.append({
                'price': row['price'],
                'units_sold': row['units_sold'],
            })

        return {
            'elasticity': avg_elasticity,
            'interpretation': interpretation,
            'chart_data': chart_data,
        }

    except Exception as e:
        return {'error': str(e)}
