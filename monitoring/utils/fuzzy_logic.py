def _norm(value, v_min, v_max):
    """
    Просте нормування в діапазон [0, 1].
    Якщо value = None -> 0, щоб не падало.
    """
    if value is None:
        return 0.0
    if v_max == v_min:
        return 0.0
    x = (float(value) - v_min) / (v_max - v_min)
    return max(0.0, min(1.0, x))


def _risk_level(score):
    """
    Перетворюємо числовий індекс [0..1] на текстову категорію.
    Тут дуже проста логіка – пізніше можна замінити на повноцінну нечітку систему.
    """
    if score < 0.33:
        return "Низький"
    elif score < 0.66:
        return "Середній"
    else:
        return "Високий"


# ---------- ПОВІТРЯ ----------

def calc_air_risk(pm25, pm10, co, no2, o3):
    """
    Повертає (risk_index, risk_label) для якості повітря.
    Діапазони – умовні, їх можна буде відкоригувати під реальні норми.
    """
    n_pm25 = _norm(pm25, 0, 75)      # мкг/м³
    n_pm10 = _norm(pm10, 0, 100)
    n_co   = _norm(co,   0, 10)      # мг/м³
    n_no2  = _norm(no2,  0, 200)
    n_o3   = _norm(o3,   0, 180)

    # Ваги параметрів – теж поки умовні
    score = (
        0.30 * n_pm25 +
        0.25 * n_pm10 +
        0.15 * n_co +
        0.15 * n_no2 +
        0.15 * n_o3
    )

    label = _risk_level(score)
    return score, label


# ---------- ВОДА ----------

def calc_water_risk(ph, nitrates, conductivity):
    """
    pH – найкраще близько 7, тому використовуємо «V-подібну» норму:
    відхилення від 7 збільшує ризик.
    """
    if ph is None:
        n_ph = 0.0
    else:
        # 6.5–8.5 – ок, за межами гірше
        deviation = abs(float(ph) - 7.0)
        n_ph = _norm(deviation, 0, 3)

    n_nitrates     = _norm(nitrates,     0, 50)    # мг/л
    n_conductivity = _norm(conductivity, 0, 800)   # мкСм/см

    score = (
        0.4 * n_ph +
        0.35 * n_nitrates +
        0.25 * n_conductivity
    )

    label = _risk_level(score)
    return score, label


# ---------- ҐРУНТ ----------

def calc_soil_risk(heavy_metals, pesticides, ph):
    if ph is None:
        n_ph = 0.0
    else:
        deviation = abs(float(ph) - 7.0)
        n_ph = _norm(deviation, 0, 3)

    n_metals     = _norm(heavy_metals, 0, 50)   # умовні одиниці
    n_pesticides = _norm(pesticides,  0, 5)

    score = (
        0.45 * n_metals +
        0.35 * n_pesticides +
        0.20 * n_ph
    )

    label = _risk_level(score)
    return score, label


# ---------- РАДІАЦІЯ ----------

def calc_radiation_risk(gamma, beta, alpha, ambient_dose_rate):
    n_gamma = _norm(gamma,            0, 0.5)   # мкЗв/год, умовно
    n_beta  = _norm(beta,             0, 0.5)
    n_alpha = _norm(alpha,            0, 0.5)
    n_dose  = _norm(ambient_dose_rate, 0, 0.3)

    score = (
        0.25 * n_gamma +
        0.20 * n_beta +
        0.20 * n_alpha +
        0.35 * n_dose
    )

    label = _risk_level(score)
    return score, label
