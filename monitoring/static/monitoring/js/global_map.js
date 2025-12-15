// ===============================
// === Колір маркерів за ризиком ===
// ===============================
function getColorByRisk(risk) {
    if (!risk) return "#999";

    const r = risk.toLowerCase();
    if (r.includes("низь") || r.includes("low")) return "#2ecc71";
    if (r.includes("серед") || r.includes("medium")) return "#f1c40f";
    if (r.includes("висок") || r.includes("high")) return "#e74c3c";
    return "#7f8c8d";
}

function makeRiskMarker(color) {
    return L.divIcon({
        className: "custom-marker",
        html: `<div style="
            width: 18px;
            height: 18px;
            background: ${color};
            border: 2px solid white;
            border-radius: 50%;
            box-shadow: 0 0 5px rgba(0,0,0,0.6);
        "></div>`,
        iconSize: [18, 18],
        iconAnchor: [9, 9]
    });
}

// ===============================
// === Рекомендації за станцією ===
// ===============================
function getAdvice(type, data) {
    const risk = (data.risk_label || "").toLowerCase();
    const text = [];

    if (type === "air") {
        if (risk.includes("висок")) {
            text.push("Уникайте тривалого перебування на вулиці.");
            text.push("Тримайте вікна закритими.");
            text.push("Використовуйте маску або респіратор на відкритому повітрі.");
        } else if (risk.includes("серед")) {
            text.push("Зменшіть активність на відкритому повітрі.");
            text.push("Провітрюйте приміщення лише у «чисті» години.");
        } else {
            text.push("Повітря в нормі. Можна займатися спортом на вулиці.");
        }
        if (data.pm25 > 150) text.push("⚠ PM2.5 значно перевищує норму! Дуже шкідливо.");
        if (data.pm10 > 200) text.push("⚠ PM10 перевищує допустимі значення.");
    }

    if (type === "water") {
        if (risk.includes("висок")) {
            text.push("Не використовуйте воду без фільтрації.");
            text.push("Уникайте пиття сирої води.");
        } else if (risk.includes("серед")) {
            text.push("Використовуйте побутовий фільтр.");
        } else {
            text.push("Якість води є задовільною.");
        }
        if (data.ph < 6.5 || data.ph > 8.5) text.push("⚠ Показник pH виходить за межі норми.");
        if (data.nitrates > 50) text.push("⚠ Високий рівень нітратів — небезпечно для здоров'я.");
    }

    if (type === "soil") {
        if (risk.includes("висок")) {
            text.push("Уникайте контакту з ґрунтом.");
            text.push("Не вирощуйте рослини на цій території.");
        } else if (risk.includes("серед")) {
            text.push("Контрольне тестування ґрунту рекомендовано.");
        } else {
            text.push("Ґрунт у безпечних межах.");
        }
        if (data.heavy_metals > 300) text.push("⚠ Висока концентрація важких металів.");
        if (data.pesticides > 100) text.push("⚠ Пестициди на небезпечному рівні.");
    }

    if (type === "radiation") {
        if (risk.includes("висок")) {
            text.push("Уникайте перебування на відкритому повітрі.");
            text.push("Тримайтеся подалі від джерел випромінювання.");
        } else if (risk.includes("серед")) {
            text.push("Зменшіть час перебування на вулиці.");
        } else {
            text.push("Радіаційний фон у межах норми.");
        }
        if (data.ambient_dose_rate > 2.0) text.push("⚠ Високий рівень радіації! Потрібні заходи безпеки.");
    }

    return text;
}

function formatDateShort(ts) {
    return new Date(ts).toLocaleString("uk-UA", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit"
    }).replace(",", "");
}

function normalizeDate(ts) {
    try {
        const d = new Date(ts);
        if (!isNaN(d.getTime())) return d.toISOString().split("T")[0];
    } catch (e) {}
    return null;
}

document.addEventListener("DOMContentLoaded", function () {
    const mapElement = document.getElementById("map");
    if (!mapElement) return;

    // -----------------------------
    // 1) Карта
    // -----------------------------
    const map = L.map("map").setView([50.45, 30.52], 5);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19 }).addTo(map);

    const layers = {
        air: L.layerGroup(),
        water: L.layerGroup(),
        soil: L.layerGroup(),
        radiation: L.layerGroup()
    };
    layers.air.addTo(map);

    // -----------------------------
    // 2) Параметри
    // -----------------------------
    const PARAM_TITLES = {
        air: { pm25: "PM2.5", pm10: "PM10", co: "CO", no2: "NO₂", o3: "O₃", risk_label: "Ризик" },
        water: { ph: "pH", nitrates: "Нітрати", conductivity: "Провідність", risk_label: "Ризик" },
        soil: { heavy_metals: "Важкі метали", pesticides: "Пестициди", ph: "pH", risk_label: "Ризик" },
        radiation: { gamma: "Gamma", beta: "Beta", alpha: "Alpha", ambient_dose_rate: "Амб. доза", risk_label: "Ризик" }
    };

    // -----------------------------
    // 3) Стан
    // -----------------------------
    let historyChart = null;
    let chartMode = "history";       // history | forecast
    let currentSelection = null;     // {type, id, data}
    let daysWindow = 3;              // 3/7/30
    let selectedDate = null;
    let globalData = null;

    // -----------------------------
    // 4) Global data
    // -----------------------------
    function fetchGlobal() {
        const url = `/api/global/?date=${selectedDate || ""}&_=${Date.now()}`;
        return fetch(url)
            .then(res => res.json())
            .then(data => {
                globalData = data;
                renderAllLayers();
            })
            .catch(err => console.error("Помилка /api/global/:", err));
    }

    function formatPopup(st, type) {
        let html = `<b>${st.name}</b><br>`;
        for (let key in PARAM_TITLES[type]) {
            if (st[key] !== undefined) html += `${PARAM_TITLES[type][key]}: ${st[key]}<br>`;
        }
        html += `<small>${formatDateShort(st.timestamp)}</small>`;
        return html;
    }

    function renderMarkers(data, layer, type) {
        layer.clearLayers();
        data.forEach(st => {
            const marker = L.marker([st.lat, st.lon], { icon: makeRiskMarker(getColorByRisk(st.risk_label)) });
            marker.bindPopup(formatPopup(st, type));
            marker.on("click", () => {
                currentSelection = { type, id: st.id, data: st };
                updateDetailsPanel(st, type);
                loadChart(type, st.id);
            });
            layer.addLayer(marker);
        });
    }

    function filterByDate(records) {
        if (!selectedDate) return records;
        return records.filter(st => normalizeDate(st.timestamp) === selectedDate);
    }

    function renderAllLayers() {
        if (!globalData) return;

        const air = filterByDate(globalData.air);
        const water = filterByDate(globalData.water);
        const soil = filterByDate(globalData.soil);
        const radiation = filterByDate(globalData.radiation);

        const total = air.length + water.length + soil.length + radiation.length;
        if (total === 0) {
            alert("Немає даних за вибрану дату!");
            return;
        }

        renderMarkers(air, layers.air, "air");
        renderMarkers(water, layers.water, "water");
        renderMarkers(soil, layers.soil, "soil");
        renderMarkers(radiation, layers.radiation, "radiation");
    }

    // -----------------------------
    // 5) Графік
    // -----------------------------
    function buildEndpoint(type, stationId) {
        if (chartMode === "forecast") {
            return `/api/forecast/${type}/${stationId}/?days=${daysWindow}&_=${Date.now()}`;
        }
        let url = `/api/history/${type}/${stationId}/?window=${daysWindow}&_=${Date.now()}`;
        if (selectedDate) url += `&date=${selectedDate}`;
        return url;
    }

    function loadChart(type, stationId) {
        if (!type || !stationId) return;

        const endpoint = buildEndpoint(type, stationId);

        fetch(endpoint)
            .then(r => r.json())
            .then(data => {
                const labels = data.timestamps || [];
                const values = data.values || [];
                const param = data.param || "";

                if (!labels.length || !values.length) {
                    console.warn("Немає даних для графіка");
                    return;
                }

                const canvas = document.getElementById("historyChart");
                if (!canvas) return;
                const ctx = canvas.getContext("2d");

                const labelName = (PARAM_TITLES[type] && PARAM_TITLES[type][param]) || param.toUpperCase();
                const isForecast = chartMode === "forecast";

                if (historyChart) historyChart.destroy();

                historyChart = new Chart(ctx, {
                    type: "line",
                    data: {
                        labels,
                        datasets: [{
                            label: labelName + (isForecast ? " (прогноз)" : ""),
                            data: values,
                            borderWidth: 2,
                            borderDash: isForecast ? [6, 6] : [],
                            tension: 0.25,
                            pointRadius: isForecast ? 0 : 2
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
            })
            .catch(err => console.error("Помилка завантаження графіка:", err));
    }

    // -----------------------------
    // 6) Панель справа
    // -----------------------------
    function updateDetailsPanel(st, type) {
        const box = document.getElementById("station-details");
        if (!box) return;

        let html = `<h5 class="fw-bold">${st.name}</h5><ul>`;
        for (let key in PARAM_TITLES[type]) {
            if (st[key] === undefined) continue;

            if (key === "risk_label") {
                const color = getColorByRisk(st[key]);
                html += `<li><b>${PARAM_TITLES[type][key]}:</b>
                    <span style="padding:4px 8px; border-radius:6px; background:${color}; color:white;">
                    ${st[key]}</span></li>`;
            } else {
                html += `<li><b>${PARAM_TITLES[type][key]}:</b> ${st[key]}</li>`;
            }
        }
        html += `</ul>`;

        const adv = getAdvice(type, st);
        if (adv.length) {
            html += `<h6 class="mt-3">Рекомендації</h6><ul>`;
            adv.forEach(a => html += `<li>${a}</li>`);
            html += `</ul><div class="text-muted small">${formatDateShort(st.timestamp)}</div>`;
        }
        box.innerHTML = html;
    }

    // -----------------------------
    // 7) Handlers
    // -----------------------------
    // перемикання шару
    document.querySelectorAll("input[name='layer']").forEach(radio => {
        radio.addEventListener("change", function () {
            Object.values(layers).forEach(l => map.removeLayer(l));
            layers[this.value].addTo(map);
        });
    });

    // перемикання history/forecast
    document.querySelectorAll("#chart-mode-global button").forEach(btn => {
        btn.addEventListener("click", function () {
            const mode = this.dataset.mode;
            if (!mode || mode === chartMode) return;

            chartMode = mode;

            document.querySelectorAll("#chart-mode-global button").forEach(b => {
                b.classList.remove("btn-primary", "active");
                b.classList.add("btn-outline-primary");
            });

            this.classList.remove("btn-outline-primary");
            this.classList.add("btn-primary", "active");

            if (currentSelection) loadChart(currentSelection.type, currentSelection.id);
        });
    });

    // кнопки 3/7/30 (одні й ті самі для двох режимів)
    document.querySelectorAll("[data-days]").forEach(btn => {
        btn.addEventListener("click", function () {
            const days = parseInt(this.dataset.days, 10);
            if (!days) return;

            daysWindow = days;

            document.querySelectorAll("[data-days]").forEach(b => {
                b.classList.remove("btn-primary", "active");
                b.classList.add("btn-outline-secondary");
            });

            this.classList.remove("btn-outline-secondary");
            this.classList.add("btn-primary", "active");

            if (currentSelection) loadChart(currentSelection.type, currentSelection.id);
        });
    });

    // фільтр по даті
    const dateInput = document.getElementById("global-date");
    const applyBtn = document.getElementById("apply-global-filter");
    if (applyBtn && dateInput) {
        applyBtn.addEventListener("click", () => {
            selectedDate = dateInput.value || null;
            fetchGlobal().then(() => {
                if (currentSelection) loadChart(currentSelection.type, currentSelection.id);
            });
        });
    }

    // старт
    fetchGlobal();
});
