import tensorflow as tf
from keras.models import Sequential
from keras.layers import LSTM, Dense
from monitoring.air.models import AirQualityRecord
from monitoring.utils.ml_helpers import prepare_series, create_sequences

def train_air_model():
    records = AirQualityRecord.objects.order_by("timestamp")
    values = [r.pm25 for r in records]  # АБО інший параметр

    arr, scaled, scaler = prepare_series(values)
    X, y = create_sequences(scaled, window=6)

    model = Sequential([
        LSTM(64, activation='tanh',return_sequences=True,input_shape=(6,1)),
        LSTM(32),
        Dense(1)
    ])

    model.compile(optimizer="adam", loss="mse")
    model.fit(X, y, epochs=25, batch_size=16, verbose=0)

    # зберігаємо
    model.save("monitoring/air/ml/air_model.h5")
    # зберігаємо scaler, щоб повернути прогноз у реальні значення
    import joblib
    joblib.dump(scaler, "monitoring/air/ml/air_scaler.pkl")

    return True
