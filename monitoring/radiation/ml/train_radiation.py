from keras.models import Sequential
from keras.layers import LSTM, Dense
from monitoring.radiation.models import RadiationRecord
from monitoring.utils.ml_helpers import prepare_series, create_sequences
import joblib

def train_radiation_model():
    records = RadiationRecord.objects.order_by("timestamp")
    values = [r.ambient_dose_rate for r in records]

    arr, scaled, scaler = prepare_series(values)
    X, y = create_sequences(scaled, window=10)

    model = Sequential([
        LSTM(50, input_shape=(10,1)),
        Dense(1)
    ])
    model.compile(optimizer="adam", loss="mse")
    model.fit(X, y, epochs=20, verbose=0)

    model.save("monitoring/radiation/ml/radiation_model.h5")
    joblib.dump(scaler, "monitoring/radiation/ml/radiation_scaler.pkl")
