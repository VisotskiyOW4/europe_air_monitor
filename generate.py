import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configuration
np.random.seed(42)
cities = [
    {"name": "Kyiv", "lat": 50.4501, "lon": 30.5234},
    {"name": "London", "lat": 51.5074, "lon": -0.1278},
    {"name": "New York", "lat": 40.7128, "lon": -74.0060},
    {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503},
    {"name": "Sydney", "lat": -33.8688, "lon": 151.2093},
    {"name": "Cairo", "lat": 30.0444, "lon": 31.2357},
    {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777}
]

end_date = datetime.now()
start_date = end_date - timedelta(days=365)
dates = pd.date_range(start=start_date, end=end_date, freq='6h')
n_timestamps = len(dates)

def generate_seasonal_data(n, base, amplitude, noise_std, anomaly_prob=0.01, anomaly_factor=3.0, seasonal_period=365*4):
    """Generates data with seasonality, noise, and anomalies."""
    # Time component for seasonality (sine wave)
    t = np.arange(n)
    seasonality = amplitude * np.sin(2 * np.pi * t / seasonal_period)
    
    # Random noise
    noise = np.random.normal(0, noise_std, n)
    
    # Combine
    data = base + seasonality + noise
    
    # Ensure non-negative values for physical parameters
    data = np.maximum(data, 0.0)
    
    # Inject anomalies
    anomalies = np.random.rand(n) < anomaly_prob
    data[anomalies] = data[anomalies] * anomaly_factor
    
    return data

# Storage for DataFrames
dfs_air = []
dfs_rad = []
dfs_soil = []
dfs_water = []

for city in cities:
    # Common columns
    base_df = pd.DataFrame({
        'name': city['name'],
        'latitude': city['lat'],
        'longitude': city['lon'],
        'timestamp': dates
    })
    
    # --- 1. Air Data ---
    # PM2.5: Higher in winter (middle of array for Northern hemisphere if starting now? Let's just simulate generic seasonality)
    # Assuming data starts a year ago.
    air_df = base_df.copy()
    air_df['pm25'] = generate_seasonal_data(n_timestamps, base=25, amplitude=10, noise_std=5, anomaly_factor=4.0)
    air_df['pm10'] = air_df['pm25'] * 1.5 + np.random.normal(0, 2, n_timestamps) # Correlation with PM2.5
    air_df['co'] = generate_seasonal_data(n_timestamps, base=0.5, amplitude=0.2, noise_std=0.1) # mg/m3
    air_df['no2'] = generate_seasonal_data(n_timestamps, base=20, amplitude=5, noise_std=3) # ppb
    air_df['o3'] = generate_seasonal_data(n_timestamps, base=40, amplitude=15, noise_std=5) # ppb, usually inverse to NO2 but simplifying
    dfs_air.append(air_df)

    # --- 2. Radiation Data ---
    # Radiation is usually very stable background with rare spikes
    rad_df = base_df.copy()
    rad_df['gamma'] = generate_seasonal_data(n_timestamps, base=0.1, amplitude=0.01, noise_std=0.01, anomaly_prob=0.005, anomaly_factor=5.0) # uSv/h
    rad_df['beta'] = generate_seasonal_data(n_timestamps, base=0.05, amplitude=0.005, noise_std=0.005) # uSv/h equivalent
    rad_df['alpha'] = np.random.exponential(0.01, n_timestamps) # Very low, sporadic
    rad_df['ambient_dose_rate'] = rad_df['gamma'] + rad_df['beta'] + rad_df['alpha']
    dfs_rad.append(rad_df)

    # --- 3. Soil Data ---
    # Soil parameters change slowly, anomalies might be spills
    soil_df = base_df.copy()
    soil_df['heavy_metals'] = generate_seasonal_data(n_timestamps, base=15, amplitude=1, noise_std=0.5, anomaly_prob=0.002, anomaly_factor=10.0) # mg/kg
    soil_df['pesticides'] = generate_seasonal_data(n_timestamps, base=0.5, amplitude=0.4, noise_std=0.1, seasonal_period=365*4/2) # Biannual spraying peaks?
    soil_df['ph'] = np.clip(np.random.normal(6.5, 0.3, n_timestamps), 4.0, 9.0) # pH is mostly stable per location
    dfs_soil.append(soil_df)

    # --- 4. Water Data ---
    water_df = base_df.copy()
    water_df['ph'] = np.clip(np.random.normal(7.2, 0.4, n_timestamps), 5.0, 9.0)
    water_df['nitrates'] = generate_seasonal_data(n_timestamps, base=10, amplitude=5, noise_std=2, anomaly_prob=0.02, anomaly_factor=3.0) # Runoff related
    water_df['conductivity'] = generate_seasonal_data(n_timestamps, base=400, amplitude=50, noise_std=20) # uS/cm
    dfs_water.append(water_df)

# Concatenate all cities
final_air = pd.concat(dfs_air, ignore_index=True)
final_rad = pd.concat(dfs_rad, ignore_index=True)
final_soil = pd.concat(dfs_soil, ignore_index=True)
final_water = pd.concat(dfs_water, ignore_index=True)

# Save to CSV
final_air.to_csv('air_monitoring_data.csv', index=False)
final_rad.to_csv('radiation_monitoring_data.csv', index=False)
final_soil.to_csv('soil_monitoring_data.csv', index=False)
final_water.to_csv('water_monitoring_data.csv', index=False)

print("Files generated successfully:")
print(f"Air: {final_air.shape}")
print(f"Radiation: {final_rad.shape}")
print(f"Soil: {final_soil.shape}")
print(f"Water: {final_water.shape}")