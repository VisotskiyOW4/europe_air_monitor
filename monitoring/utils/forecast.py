import numpy as np
import tensorflow as tf
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler

def lstm_forecast(data, steps=24):
    """
    data: масив/список історичних значень
    steps: на скільки кроків вперед прогнозуємо
    """

    # 👉 Захист на випадок, якщо даних мало
    if len(data) < 12:
        return [float(data[-1])] * steps

    # 👉 Масштабування
    values = np.array(data, dtype=float).reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(values)

    # 👉 Формуємо вікно для LSTM (чим більше даних — тим довше вікно)
    window = max(5, len(data) // 12)

    X, y = [], []
    for i in range(len(scaled) - window):
        X.append(scaled[i:i+window])
        y.append(scaled[i+window][0])

    X, y = np.array(X), np.array(y)

    # 👉 Модель LSTM (з Dropout — проти перенавчання)
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(window, 1)),
        Dropout(0.2),
        LSTM(32),
        Dense(1)
    ])

    model.compile(optimizer='adam', loss='mse')

    # 👉 Навчання (трохи довше = реалістичніший результат)
    model.fit(X, y, epochs=40, batch_size=8, verbose=0)

    # 👉 Прогнозування по одному кроку вперед
    last = scaled[-window:]
    preds = []

    for _ in range(steps):
        pred = model.predict(last.reshape(1, window, 1), verbose=0)[0][0]
        preds.append(pred)
        last = np.vstack((last[1:], [[pred]]))

    # 👉 Повертаємо до нормального масштабу
    return scaler.inverse_transform(np.array(preds).reshape(-1, 1)).flatten().tolist()
