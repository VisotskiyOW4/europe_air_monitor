import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# --- 1. Вхідні змінні ---
pm25 = ctrl.Antecedent(np.arange(0, 101, 1), 'pm25')
pm10 = ctrl.Antecedent(np.arange(0, 151, 1), 'pm10')
co = ctrl.Antecedent(np.arange(0, 11, 0.1), 'co')
no2 = ctrl.Antecedent(np.arange(0, 201, 1), 'no2')
o3 = ctrl.Antecedent(np.arange(0, 201, 1), 'o3')

# --- 2. Вихідна змінна ---
aqi = ctrl.Consequent(np.arange(0, 101, 1), 'aqi')

# --- 3. Функції належності ---
pm25['low'] = fuzz.trapmf(pm25.universe, [0, 0, 15, 35])
pm25['medium'] = fuzz.trimf(pm25.universe, [25, 50, 75])
pm25['high'] = fuzz.trapmf(pm25.universe, [60, 80, 100, 100])

pm10['low'] = fuzz.trapmf(pm10.universe, [0, 0, 25, 50])
pm10['medium'] = fuzz.trimf(pm10.universe, [40, 75, 100])
pm10['high'] = fuzz.trapmf(pm10.universe, [90, 120, 150, 150])

co['low'] = fuzz.trapmf(co.universe, [0, 0, 1, 3])
co['medium'] = fuzz.trimf(co.universe, [2, 4, 6])
co['high'] = fuzz.trapmf(co.universe, [5, 7, 10, 10])

no2['low'] = fuzz.trapmf(no2.universe, [0, 0, 40, 80])
no2['medium'] = fuzz.trimf(no2.universe, [60, 100, 140])
no2['high'] = fuzz.trapmf(no2.universe, [120, 160, 200, 200])

o3['low'] = fuzz.trapmf(o3.universe, [0, 0, 40, 80])
o3['medium'] = fuzz.trimf(o3.universe, [70, 100, 130])
o3['high'] = fuzz.trapmf(o3.universe, [120, 160, 200, 200])

aqi['good'] = fuzz.trapmf(aqi.universe, [0, 0, 30, 50])
aqi['moderate'] = fuzz.trimf(aqi.universe, [40, 60, 80])
aqi['poor'] = fuzz.trapmf(aqi.universe, [70, 85, 100, 100])

# --- 4. Правила нечіткої логіки ---
rule1 = ctrl.Rule(pm25['low'] & pm10['low'] & co['low'] & no2['low'] & o3['low'], aqi['good'])
rule2 = ctrl.Rule(pm25['medium'] | pm10['medium'] | co['medium'] | no2['medium'] | o3['medium'], aqi['moderate'])
rule3 = ctrl.Rule(pm25['high'] | pm10['high'] | co['high'] | no2['high'] | o3['high'], aqi['poor'])

# --- 5. Створення контролера ---
aqi_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
aqi_simulator = ctrl.ControlSystemSimulation(aqi_ctrl)

def calculate_aqi(pm25_val, pm10_val, co_val, no2_val, o3_val):
    """Обчислення нечіткого AQI"""
    aqi_simulator.input['pm25'] = pm25_val
    aqi_simulator.input['pm10'] = pm10_val
    aqi_simulator.input['co'] = co_val
    aqi_simulator.input['no2'] = no2_val
    aqi_simulator.input['o3'] = o3_val

    aqi_simulator.compute()
    return round(aqi_simulator.output['aqi'], 2)
