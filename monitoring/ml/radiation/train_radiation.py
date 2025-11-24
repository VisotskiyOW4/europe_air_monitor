import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import pickle
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "radiation_monitoring_data.csv")


def train_radiation_model():

    print("=== TRAINING RADIATION MODEL (LSTM) ===")

    df = pd.read_csv(DATA_PATH)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    # Основний показник — ambient_dose_rate (найважливіший)
    values = df["ambient_dose_rate"].values.reshape(-1, 1)

    scaler = MinMaxScaler()
    values_norm = scaler.fit_transform(values)

    SEQ = 24  # вікно = одна доба
    X, y = [], []

    for i in range(len(values_norm) - SEQ):
        X.append(values_norm[i:i+SEQ])
        y.append(values_norm[i+SEQ])

    X = np.array(X)
    y = np.array(y)

    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(64, return_sequences=True, input_shape=(SEQ, 1)),
        tf.keras.layers.LSTM(32),
        tf.keras.layers.Dense(1)
    ])

    model.compile(optimizer="adam", loss="mse")
    model.fit(X, y, epochs=8, batch_size=32)

    # Зберігаємо модель
    model.save(os.path.join(BASE_DIR, "radiation_model.h5"))

    # Зберігаємо scaler
    with open(os.path.join(BASE_DIR, "radiation_scaler.pkl"), "wb") as f:
        pickle.dump(scaler, f)

    print("=== ✔ RADIATION MODEL TRAINED AND SAVED ===")


if __name__ == "__main__":
    train_radiation_model()
