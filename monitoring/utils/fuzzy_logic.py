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


# ----------------------------------------
# Універсальна функція для витягування полів
# ----------------------------------------
def get(st, field):
    """Дістає значення з ORM-об’єкта або dict"""
    if isinstance(st, dict):
        return st.get(field)
    return getattr(st, field)


# ---------------------------------------------------------
# 1) НЕЧІТКА ЛОГІКА ДЛЯ ПОВІТРЯ
# ---------------------------------------------------------

def calc_air_risk(st):

    pm25 = normalize(get(st, "pm25"), 0, 150)
    pm10 = normalize(get(st, "pm10"), 0, 200)
    co = normalize(get(st, "co"), 0, 15)
    no2 = normalize(get(st, "no2"), 0, 200)
    o3 = normalize(get(st, "o3"), 0, 200)

    score = (
        pm25 * 0.35 +
        pm10 * 0.25 +
        co * 0.15 +
        no2 * 0.15 +
        o3 * 0.10
    )

    return {
        "risk_score": round(score, 3),
        "risk_label": risk_label(score),
    }


# ---------------------------------------------------------
# 2) НЕЧІТКА ЛОГІКА ДЛЯ ВОДИ
# ---------------------------------------------------------

def calc_water_risk(st):

    ph = normalize(abs(get(st, "ph") - 7), 0, 7)
    nitrates = normalize(get(st, "nitrates"), 0, 100)
    conductivity = normalize(get(st, "conductivity"), 0, 2000)

    score = ph * 0.4 + nitrates * 0.35 + conductivity * 0.25

    return {
        "risk_score": round(score, 3),
        "risk_label": risk_label(score),
    }


# ---------------------------------------------------------
# 3) НЕЧІТКА ЛОГІКА ДЛЯ ҐРУНТУ
# ---------------------------------------------------------

def calc_soil_risk(st):

    heavy = normalize(get(st, "heavy_metals"), 0, 500)
    pesticides = normalize(get(st, "pesticides"), 0, 200)
    ph = normalize(abs(get(st, "ph") - 7), 0, 7)

    score = heavy * 0.45 + pesticides * 0.35 + ph * 0.20

    return {
        "risk_score": round(score, 3),
        "risk_label": risk_label(score),
    }


# ---------------------------------------------------------
# 4) НЕЧІТКА ЛОГІКА ДЛЯ РАДІАЦІЇ
# ---------------------------------------------------------

def calc_radiation_risk(st):

    gamma = normalize(get(st, "gamma"), 0, 1.0)
    beta = normalize(get(st, "beta"), 0, 2.0)
    alpha = normalize(get(st, "alpha"), 0, 0.5)
    dose = normalize(get(st, "ambient_dose_rate"), 0, 5.0)

    score = (
        gamma * 0.35 +
        beta * 0.25 +
        alpha * 0.15 +
        dose * 0.25
    )

    return {
        "risk_score": round(score, 3),
        "risk_label": risk_label(score),
    }
