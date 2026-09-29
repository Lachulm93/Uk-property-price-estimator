import duckdb
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import root_mean_squared_error, r2_score
import lightgbm as lgb

def train():
    print("Loading data from DuckDB...")
    con = duckdb.connect("data/properties.duckdb")
    
    # Extract clean training subset
    # Extract postcode outward code (e.g., 'SW1A 1AA' -> 'SW1A') to generalize location
    df = con.execute("""
        SELECT 
            price,
            property_type,
            is_new_build,
            tenure,
            SPLIT_PART(postcode, ' ', 1) AS postcode_area,
            town_city
        FROM sales
        WHERE price BETWEEN 40000 AND 2500000
    """).df()
    con.close()

    print(f"Training on {len(df):,} transactions...")

    # Filter to frequent areas to avoid sparse categories
    top_areas = df['postcode_area'].value_counts()
    valid_areas = top_areas[top_areas >= 5].index
    df = df[df['postcode_area'].isin(valid_areas)]

    X = df[['property_type', 'is_new_build', 'tenure', 'postcode_area']]
    # Predict log(price) to handle UK property price skewness
    y = np.log1p(df['price'])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    categorical_features = ['property_type', 'is_new_build', 'tenure', 'postcode_area']
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ]
    )

    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', lgb.LGBMRegressor(n_estimators=150, learning_rate=0.08, random_state=42, verbose=-1))
    ])

    print("Fitting LightGBM model...")
    model.fit(X_train, y_train)

    # Evaluation
    preds = model.predict(X_test)
    r2 = r2_score(y_test, preds)
    rmse = root_mean_squared_error(np.expm1(y_test), np.expm1(preds))
    print(f"Model Performance: R^2 Score = {r2:.3f}, RMSE = £{rmse:,.0f}")

    joblib.dump(model, "data/property_model.joblib")
    print("Model saved to data/property_model.joblib!")

if __name__ == "__main__":
    train()