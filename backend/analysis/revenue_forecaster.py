import pandas as pd
import numpy as np
from prophet import Prophet
import warnings
warnings.filterwarnings('ignore')

def forecast_revenue(df):
    """
    Facebook Prophet model to forecast
    future revenue trends
    """
    try:
        df = df.copy()

        # Prophet requires columns named 'ds' and 'y'
        if 'date' not in df.columns:
            return {"error": "Date column is required for revenue forecasting"}

        # Create revenue column
        df['revenue'] = df['price'] * df['units_sold']

        # Prepare data for Prophet
        prophet_df = pd.DataFrame({
            'ds': pd.to_datetime(df['date']),
            'y': df['revenue']
        })

        # Remove duplicates and sort
        prophet_df = prophet_df.drop_duplicates(subset='ds')
        prophet_df = prophet_df.sort_values('ds')

        # Train Prophet model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            interval_width=0.95
        )
        model.fit(prophet_df)

        # Forecast next 30 days
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)

        # Historical chart data
        historical_chart = []
        for _, row in prophet_df.tail(60).iterrows():
            historical_chart.append({
                "date": str(row['ds'].date()),
                "actual_revenue": round(float(row['y']), 2)
            })

        # Forecast chart data
        forecast_chart = []
        future_forecast = forecast.tail(30)
        for _, row in future_forecast.iterrows():
            forecast_chart.append({
                "date": str(row['ds'].date()),
                "predicted_revenue": round(float(row['yhat']), 2),
                "lower_bound": round(float(row['yhat_lower']), 2),
                "upper_bound": round(float(row['yhat_upper']), 2)
            })

        # Summary stats
        avg_predicted = round(float(future_forecast['yhat'].mean()), 2)
        avg_historical = round(float(prophet_df['y'].mean()), 2)
        growth_pct = round(((avg_predicted - avg_historical) / avg_historical) * 100, 2)

        return {
            "historical_chart": historical_chart,
            "forecast_chart": forecast_chart,
            "summary": {
                "avg_historical_revenue": avg_historical,
                "avg_predicted_revenue": avg_predicted,
                "growth_pct": growth_pct,
                "forecast_period": "Next 30 days",
                "interpretation": "Revenue is expected to grow" if growth_pct > 0 else "Revenue is expected to decline"
            }
        }

    except Exception as e:
        return {"error": str(e)}