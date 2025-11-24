import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "soil_monitoring_data.csv")


def train_soil_model():

    print("=== TRAINING SOIL MODEL (Random Forest) ===")

    df = pd.read_csv(DATA_PATH)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    # Робимо індекс часу
    df["t"] = np.arange(len(df))

    # Вибираємо ключові фічі
    X = df[["t", "heavy_metals", "pesticides"]]
    y = df["ph"]

    # Масштабуємо pH
    scaler = MinMaxScaler()
    y_norm = scaler.fit_transform(y.values.reshape(-1, 1)).flatten()

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=12,
        random_state=42
    )

    model.fit(X, y_norm)

    # Зберігаємо модель
    with open(os.path.join(BASE_DIR, "soil_model.pkl"), "wb") as f:
        pickle.dump(model, f)

    # Зберігаємо scaler
    with open(os.path.join(BASE_DIR, "soil_scaler.pkl"), "wb") as f:
        pickle.dump(scaler, f)

    print("=== ✔ SOIL MODEL TRAINED AND SAVED ===")


if __name__ == "__main__":
    train_soil_model()
