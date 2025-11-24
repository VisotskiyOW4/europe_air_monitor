import numpy as np
import joblib
from keras.models import load_model


# ===============================
# 🔹 1. Завантаження LSTM/GRU моделі
# ===============================
def load_lstm_model(path):
    """Load a trained LSTM/GRU model (.h5)."""
    try:
        model = load_model(path)
        return model
    except Exception as e:
        print("Error loading model:", e)
        return None


# ===============================
# 🔹 2. Підготовка даних до LSTM
# ===============================
def prepare_lstm_data(values, seq_len=30):
    """
    Convert array into LSTM windows:
    [x0, x1, ... x29] → predict x30
    """
    data = []
    for i in range(len(values) - seq_len):
        data.append(values[i:i + seq_len])

    return np.array(data)


# ===============================
# 🔹 3. Завантаження StandardScaler/MinMaxScaler
# ===============================
def load_scaler(path):
    """Load a sklearn scaler (.pkl)."""
    try:
        scaler = joblib.load(path)
        return scaler
    except Exception as e:
        print("Error loading scaler:", e)
        return None


# ===============================
# 🔹 4. Прогноз майбутніх точок
# ===============================
def predict_future(model, last_values, scaler, steps=48):
    """
    model        — LSTM model
    last_values  — останні сирі значення (масив)
    scaler       — MinMaxScaler / StandardScaler
    steps        — кількість прогнозів

    Повертає масив прогнозів.
    """

    seq_len = len(last_values)
    x = np.array(last_values).reshape(1, seq_len, 1)

    preds = []

    for _ in range(steps):
        scaled = scaler.transform(x.reshape(-1, 1)).reshape(1, seq_len, 1)

        y_pred = model.predict(scaled, verbose=0)
        y_inv = scaler.inverse_transform(y_pred)[0][0]

        preds.append(y_inv)

        x = np.roll(x, -1)
        x[0, -1, 0] = y_inv

    return preds
