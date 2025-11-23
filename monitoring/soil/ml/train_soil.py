from sklearn.ensemble import RandomForestRegressor
from monitoring.soil.models import SoilQualityRecord
import joblib

def train_soil_model():
    records = SoilQualityRecord.objects.order_by("timestamp")
    X = [[r.heavy_metals, r.pesticides] for r in records]  # можна додати ph
    y = [r.ph for r in records]

    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)

    joblib.dump(model, "monitoring/soil/ml/soil_model.pkl")
