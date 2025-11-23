from keras.models import Sequential
from keras.layers import GRU, Dense
from monitoring.water.models import WaterQualityRecord
from monitoring.utils.ml_helpers import prepare_series, create_sequences
import joblib

def train_water_model():
    records = WaterQualityRecord.objects.order_by("timestamp")
    values = [r.ph for r in records]  # ключовий параметр

    arr, scaled, scaler = prepare_series(values)
    X, y = create_sequences(scaled, window=4)

    model = Sequential([
        GRU(32, activation='tanh', input_shape=(4,1)),
        Dense(1)
    ])
    model.compile(optimizer="adam", loss="mse")
    model.fit(X, y, epochs=20, verbose=0)

    model.save("monitoring/water/ml/water_model.h5")
    joblib.dump(scaler, "monitoring/water/ml/water_scaler.pkl")
