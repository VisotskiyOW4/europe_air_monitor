# monitoring/utils/fuzzy_logic.py

def normalize(value, min_val, max_val):
    """Нормалізація в діапазон 0–1"""
    if value is None:
        return 0
    return max(0, min(1, (value - min_val) / (max_val - min_val)))


def risk_label(score):
    """Перетворення ризику в текстову метку"""
    if score < 0.33:
        return "Низький"
    elif score < 0.66:
        return "Середній"
    return "Високий"


# ---------------------------------------------------------
# 1) НЕЧІТКА ЛОГІКА ДЛЯ ПОВІТРЯ
# ---------------------------------------------------------

def calc_air_risk(st):
    """
    st — dict із полями: pm25, pm10, co, no2, o3
    """

    pm25 = normalize(st["pm25"], 0, 150)
    pm10 = normalize(st["pm10"], 0, 200)
    co = normalize(st["co"], 0, 15)
    no2 = normalize(st["no2"], 0, 200)
    o3 = normalize(st["o3"], 0, 200)

    score = (pm25 * 0.35 +
             pm10 * 0.25 +
             co * 0.15 +
             no2 * 0.15 +
             o3 * 0.10)

    return {
        "risk_score": round(score, 3),
        "risk_label": risk_label(score),
    }


# ---------------------------------------------------------
# 2) НЕЧІТКА ЛОГІКА ДЛЯ ВОДИ
# ---------------------------------------------------------

def calc_water_risk(st):
    ph = normalize(abs(st["ph"] - 7), 0, 7)  # відхилення від норми
    nitrates = normalize(st["nitrates"], 0, 100)
    conductivity = normalize(st["conductivity"], 0, 2000)

    score = ph * 0.4 + nitrates * 0.35 + conductivity * 0.25

    return {
        "risk_score": round(score, 3),
        "risk_label": risk_label(score),
    }


# ---------------------------------------------------------
# 3) НЕЧІТКА ЛОГІКА ДЛЯ ҐРУНТУ
# ---------------------------------------------------------

def calc_soil_risk(st):
    heavy = normalize(st["heavy_metals"], 0, 500)
    pest = normalize(st["pesticides"], 0, 200)
    ph = normalize(abs(st["ph"] - 7), 0, 7)

    score = heavy * 0.45 + pest * 0.35 + ph * 0.20

    return {
        "risk_score": round(score, 3),
        "risk_label": risk_label(score),
    }


# ---------------------------------------------------------
# 4) НЕЧІТКА ЛОГІКА ДЛЯ РАДІАЦІЇ
# ---------------------------------------------------------

def calc_radiation_risk(st):
    gamma = normalize(st["gamma"], 0, 1.0)
    beta = normalize(st["beta"], 0, 2.0)
    alpha = normalize(st["alpha"], 0, 0.5)
    dose = normalize(st["ambient_dose_rate"], 0, 5.0)

    score = gamma * 0.35 + beta * 0.25 + alpha * 0.15 + dose * 0.25

    return {
        "risk_score": round(score, 3),
        "risk_label": risk_label(score),
    }
