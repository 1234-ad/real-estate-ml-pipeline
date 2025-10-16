"""Train a LightGBM model on the processed data and output metrics.

Saves a trained model as `models/lgb_model.pkl` and prints R2 and RMSE.
"""
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import joblib

# Try to import LightGBM; fall back to RandomForest if not available so script
# runs in environments where LightGBM isn't installed.
try:
    import lightgbm as lgb
    _HAS_LGB = True
except Exception:
    from sklearn.ensemble import RandomForestRegressor
    _HAS_LGB = False


def load_data(path='data/processed/scraped_data.csv'):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Processed data not found at {p}. Run data_cleaner or generate data first.")
    return pd.read_csv(p)


def prepare_features(df: pd.DataFrame):
    df = df.copy()
    # Basic feature selection
    features = ['area_sqft','bhk','amenity_count','maintenance','deposit','floor','total_floors','floor_ratio']
    X = df[features].fillna(-1)
    y = df['rent_per_month']
    return X, y


def train(X_train, y_train, X_val, y_val):
    if _HAS_LGB:
        train_data = lgb.Dataset(X_train, label=y_train)
        val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
        params = {
            'objective': 'regression',
            'metric': 'rmse',
            'verbosity': -1,
            'boosting_type': 'gbdt',
            'learning_rate': 0.05,
            'num_leaves': 31
        }
        model = lgb.train(params, train_data, valid_sets=[val_data], early_stopping_rounds=20, num_boost_round=1000)
        model._model_type = 'lightgbm'
        return model
    else:
        # Fallback: RandomForestRegressor
        print("LightGBM not available; training RandomForestRegressor as fallback.")
        rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        rf._model_type = 'random_forest'
        return rf


def main():
    df = load_data()
    X, y = prepare_features(df)
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    model = train(X_train, y_train, X_val, y_val)
    # Predict depending on model type
    if hasattr(model, '_model_type') and model._model_type == 'lightgbm':
        preds = model.predict(X_val, num_iteration=model.best_iteration)
    else:
        preds = model.predict(X_val)
    r2 = r2_score(y_val, preds)
    rmse = float(np.sqrt(mean_squared_error(y_val, preds)))
    print(f"Validation R2: {r2:.4f}, RMSE: {rmse:.2f}")

    out_dir = Path('models')
    out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out_dir / 'lgb_model.pkl')
    print(f"Saved model to {out_dir / 'lgb_model.pkl'}")


if __name__ == '__main__':
    main()
