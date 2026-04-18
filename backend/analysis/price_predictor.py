import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

def predict_optimal_price(df):
    """
    XGBoost model to predict optimal price
    that maximizes revenue
    """
    try:
        # Feature Engineering
        df = df.copy()

        # Create time based features if date exists
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df['month'] = df['date'].dt.month
            df['day_of_week'] = df['date'].dt.dayofweek
            df['quarter'] = df['date'].dt.quarter
        else:
            df['month'] = 1
            df['day_of_week'] = 1
            df['quarter'] = 1

        # Create lag features
        df['price_lag1'] = df['price'].shift(1).fillna(df['price'].mean())
        df['units_lag1'] = df['units_sold'].shift(1).fillna(df['units_sold'].mean())

        # Create rolling features
        df['price_rolling_mean'] = df['price'].rolling(7, min_periods=1).mean()
        df['units_rolling_mean'] = df['units_sold'].rolling(7, min_periods=1).mean()

        # Price to competitor ratio
        df['price_ratio'] = df['price'] / df['competitor_price']

        # Target variable — revenue
        df['revenue'] = df['price'] * df['units_sold']

        # Features
        features = [
            'price', 'competitor_price', 'month',
            'day_of_week', 'quarter', 'price_lag1',
            'units_lag1', 'price_rolling_mean',
            'units_rolling_mean', 'price_ratio'
        ]

        X = df[features]
        y = df['revenue']

        # Train test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train XGBoost model
        model = XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42,
            verbosity=0
        )
        model.fit(X_train, y_train)

        # Evaluate model
        y_pred = model.predict(X_test)
        rmse = round(np.sqrt(mean_squared_error(y_test, y_pred)), 2)
        r2 = round(r2_score(y_test, y_pred), 4)

        # Find optimal price using model
        price_range = np.linspace(
            df['price'].min(),
            df['price'].max(),
            100
        )

        best_price = None
        best_revenue = 0

        avg_row = X.mean().to_dict()

        for price in price_range:
            test_row = avg_row.copy()
            test_row['price'] = price
            test_row['price_ratio'] = price / avg_row['competitor_price']
            pred_revenue = model.predict(pd.DataFrame([test_row]))[0]
            if pred_revenue > best_revenue:
                best_revenue = pred_revenue
                best_price = price

        # Feature importance
        importance = dict(zip(features, model.feature_importances_))
        top_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "optimal_price": round(float(best_price), 2),
            "predicted_revenue": round(float(best_revenue), 2),
            "model_accuracy": {
                "rmse": float(rmse),
                "r2_score": float(r2),
                "accuracy_pct": round(float(r2) * 100, 2)
            },
            "top_features": [
                {"feature": f, "importance": round(float(i), 4)}
                for f, i in top_features
            ],
            "current_avg_price": round(float(df['price'].mean()), 2),
            "current_avg_revenue": round(float(df['revenue'].mean()), 2)
        }

    except Exception as e:
        return {"error": str(e)}