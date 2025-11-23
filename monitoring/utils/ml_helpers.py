import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def prepare_series(values):
    """Перетворення списку чисел у numpy + зміну форми."""
    arr = np.array(values, dtype='float32').reshape(-1, 1)
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(arr)
    return arr, scaled, scaler

def create_sequences(data, window=5):
    X, y = [], []
    for i in range(len(data) - window):
        X.append(data[i:i+window])
        y.append(data[i+window][0])
    return np.array(X), np.array(y)
