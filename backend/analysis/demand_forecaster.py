import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

def forecast_demand(df):
    """
    Random Forest model to predict demand (units sold)
    at different price points
    """
    try:
        df = df.copy()

        # Feature Engineering
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df['month'] = df['date'].dt.month
            df['day_of_week'] = df['date'].dt.dayofweek
            df['quarter'] = df['date'].dt.quarter
        else:
            df['month'] = 1
            df['day_of_week'] = 1
            df['quarter'] = 1

        # Lag features
        df['price_lag1'] = df['price'].shift(1).fillna(df['price'].mean())
        df['units_lag1'] = df['units_sold'].shift(1).fillna(df['units_sold'].mean())

        # Rolling features
        df['price_rolling_mean'] = df['price'].rolling(7, min_periods=1).mean()
        df['units_rolling_mean'] = df['units_sold'].rolling(7, min_periods=1).mean()

        # Price ratio
        df['price_ratio'] = df['price'] / df['competitor_price']

        # Features and target
        features = [
            'price', 'competitor_price', 'month',
            'day_of_week', 'quarter', 'price_lag1',
            'units_lag1', 'price_rolling_mean',
            'units_rolling_mean', 'price_ratio'
        ]

        X = df[features]
        y = df['units_sold']

        # Train test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train Random Forest model
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)

        # Evaluate model
        y_pred = model.predict(X_test)
        rmse = round(np.sqrt(mean_squared_error(y_test, y_pred)), 2)
        r2 = round(r2_score(y_test, y_pred), 4)

        # Predict demand at different price points
        price_range = np.linspace(
            df['price'].min(),
            df['price'].max(),
            20
        )

        avg_row = X.mean().to_dict()
        demand_chart = []

        for price in price_range:
            test_row = avg_row.copy()
            test_row['price'] = price
            test_row['price_ratio'] = price / avg_row['competitor_price']
            predicted_units = model.predict(pd.DataFrame([test_row]))[0]
            demand_chart.append({
                "price": round(float(price), 2),
                "predicted_units": round(float(predicted_units), 0)
            })

        # Feature importance
        importance = dict(zip(features, model.feature_importances_))
        top_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:5]

        # Next month demand prediction
        last_row = X.iloc[-1].to_dict()
        next_month_demand = model.predict(pd.DataFrame([last_row]))[0]

        return {
            "model_accuracy": {
                "rmse": float(rmse),
                "r2_score": float(r2),
                "accuracy_pct": round(float(r2) * 100, 2)
            },
            "next_month_demand": round(float(next_month_demand), 0),
            "current_avg_demand": round(float(df['units_sold'].mean()), 0),
            "demand_chart": demand_chart,
            "top_features": [
                {"feature": f, "importance": round(float(i), 4)}
                for f, i in top_features
            ]
        }

    except Exception as e:
        return {"error": str(e)}