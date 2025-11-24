import joblib

def load_scaler(path):
    """
    Load a MinMaxScaler / StandardScaler from .pkl file.
    """
    try:
        scaler = joblib.load(path)
        return scaler
    except Exception as e:
        print(f"Error loading scaler from {path}: {e}")
        return None
