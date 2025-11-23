import os
import numpy as np
import django
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")
django.setup()

from monitoring.air.models import AirQualityRecord
from monitoring.water.models import WaterQualityRecord
from monitoring.soil.models import SoilQualityRecord
from monitoring.radiation.models import RadiationRecord


def train_model(values, save_path):
    if len(values) < 20:
        print("Не достатньо даних для тренування: ", save_path)
        return

    values = np.array(values).reshape(-1,1)
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(values)

    X, y = [], []
    window = 10
    for i in range(len(scaled)-window):
        X.append(scaled[i:i+window])
        y.append(scaled[i+window][0])

    X, y = np.array(X), np.array(y)

    model = Sequential([
        LSTM(50, activation='tanh', input_shape=(window,1)),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=30, batch_size=16, verbose=1)

    model.save(save_path)
    np.save(save_path+"_scaler.npy", scaler.data_max_)


def train_all():
    base_dir = "monitoring/ml_models/"

    # === Повітря (PM2.5) ===
    values = list(AirQualityRecord.objects.values_list("pm25", flat=True))
    train_model(values, base_dir + "air_lstm.keras")

    # === Вода (pH) ===
    values = list(WaterQualityRecord.objects.values_list("ph", flat=True))
    train_model(values, base_dir + "water_lstm.keras")

    # === Ґрунт (heavy_metals) ===
    values = list(SoilQualityRecord.objects.values_list("heavy_metals", flat=True))
    train_model(values, base_dir + "soil_lstm.keras")

    # === Радіація (ambient_dose_rate) ===
    values = list(RadiationRecord.objects.values_list("ambient_dose_rate", flat=True))
    train_model(values, base_dir + "radiation_lstm.keras")


if __name__ == "__main__":
    train_all()
