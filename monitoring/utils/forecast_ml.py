import os
import pickle
import numpy as np
from datetime import timedelta

from django.conf import settings
from keras.models import load_model


# Кеш, щоб не вантажити модель при кожному запиті
_MODEL_CACHE = {}


def _get_path(*parts):
    """
    Зручний хелпер: формує абсолютний шлях від BASE_DIR
    """
    return os.path.join(settings.BASE_DIR, *parts)


# ============================
#  ЗАВАНТАЖЕННЯ МОДЕЛЕЙ
# ============================

def get_air_model():
    if "air" not in _MODEL_CACHE:
        model_path = _get_path("ml", "air", "air_model.h5")
        scaler_path = _get_path("ml", "air", "air_scaler.pkl")

        model = load_model(model_path)
        with open(scaler_path, "rb") as f:
            scaler = pickle.load(f)

        _MODEL_CACHE["air"] = (model, scaler)

    return _MODEL_CACHE["air"]


def get_water_model():
    if "water" not in _MODEL_CACHE:
        model_path = _get_path("ml", "water", "water_model.h5")
        scaler_path = _get_path("ml", "water", "water_scaler.pkl")

        model = load_model(model_path)
        with open(scaler_path, "rb") as f:
            scaler = pickle.load(f)

        _MODEL_CACHE["water"] = (model, scaler)

    return _MODEL_CACHE["water"]


def get_soil_model():
    if "soil" not in _MODEL_CACHE:
        model_path = _get_path("ml", "soil", "soil_model.pkl")
        scaler_path = _get_path("ml", "soil", "soil_scaler.pkl")

        with open(model_path, "rb") as f:
            model = pickle.load(f)
        with open(scaler_path, "rb") as f:
            scaler = pickle.load(f)

        _MODEL_CACHE["soil"] = (model, scaler)

    return _MODEL_CACHE["soil"]


def get_radiation_model():
    if "radiation" not in _MODEL_CACHE:
        model_path = _get_path("ml", "radiation", "radiation_model.h5")
        scaler_path = _get_path("ml", "radiation", "radiation_scaler.pkl")

        model = load_model(model_path)
        with open(scaler_path, "rb") as f:
            scaler = pickle.load(f)

        _MODEL_CACHE["radiation"] = (model, scaler)

    return _MODEL_CACHE["radiation"]


# ============================
#  ФУНКЦІЇ ПРОГНОЗУ
# ============================

def forecast_air(values, days, points_per_day=4):
    """
    values: список останніх значень pm25 для станції
    days:  на скільки днів прогнозувати
    points_per_day: скільки вимірів на добу (у тебе 4, кожні 6 годин)
    """
    model, scaler = get_air_model()

    seq = 24  # такий самий, як у train_air.py
    if len(values) < seq:
        # замало даних для прогнозу
        return []

    arr = np.array(values[-seq:], dtype=float).reshape(-1, 1)
    norm = scaler.transform(arr)

    steps = int(days * points_per_day)

    preds_scaled = []
    window = norm.copy()

    for _ in range(steps):
        p = model.predict(window.reshape(1, seq, 1), verbose=0)[0, 0]
        preds_scaled.append(p)
        window = np.vstack([window[1:], [[p]]])

    preds = scaler.inverse_transform(np.array(preds_scaled).reshape(-1, 1)).flatten().tolist()
    return preds


def forecast_water(values, days, points_per_day=4):
    """
    Прогнозуємо pH води (аналогічно air).
    """
    model, scaler = get_water_model()

    seq = 24
    if len(values) < seq:
        return []

    arr = np.array(values[-seq:], dtype=float).reshape(-1, 1)
    norm = scaler.transform(arr)

    steps = int(days * points_per_day)

    preds_scaled = []
    window = norm.copy()

    for _ in range(steps):
        p = model.predict(window.reshape(1, seq, 1), verbose=0)[0, 0]
        preds_scaled.append(p)
        window = np.vstack([window[1:], [[p]]])

    preds = scaler.inverse_transform(np.array(preds_scaled).reshape(-1, 1)).flatten().tolist()
    return preds


def forecast_soil(last_heavy_metals, last_pesticides, last_index, days):
    """
    RandomForest для ґрунту:
    - як фічі: t (індекс часу), heavy_metals, pesticides
    - прогнозуємо pH на кожен наступний день
    """
    model, scaler = get_soil_model()

    steps = int(days)
    X_future = []
    for i in range(1, steps + 1):
        t = last_index + i
        X_future.append([t, float(last_heavy_metals), float(last_pesticides)])

    X_future = np.array(X_future)
    preds_norm = model.predict(X_future)
    preds = scaler.inverse_transform(np.array(preds_norm).reshape(-1, 1)).flatten().tolist()
    return preds


def forecast_radiation(values, days, points_per_day=4):
    """
    Прогноз амбієнтної дози (ambient_dose_rate).
    """
    model, scaler = get_radiation_model()

    seq = 24
    if len(values) < seq:
        return []

    arr = np.array(values[-seq:], dtype=float).reshape(-1, 1)
    norm = scaler.transform(arr)

    steps = int(days * points_per_day)

    preds_scaled = []
    window = norm.copy()

    for _ in range(steps):
        p = model.predict(window.reshape(1, seq, 1), verbose=0)[0, 0]
        preds_scaled.append(p)
        window = np.vstack([window[1:], [[p]]])

    preds = scaler.inverse_transform(np.array(preds_scaled).reshape(-1, 1)).flatten().tolist()
    return preds
