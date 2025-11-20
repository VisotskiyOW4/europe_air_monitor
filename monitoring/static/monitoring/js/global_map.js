// ===============================
// === Колір маркерів за ризиком ===
// ===============================
function getColorByRisk(risk) {
    if (!risk) return "#999";

    const r = risk.toLowerCase();
    if (r.includes("низь") || r.includes("low")) return "#2ecc71";      // зелений
    if (r.includes("серед") || r.includes("medium")) return "#f1c40f";  // жовтий
    if (r.includes("висок") || r.includes("high")) return "#e74c3c";    // червоний
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

    // ---- AIR ----
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

    // ---- WATER ----
    if (type === "water") {
        if (risk.includes("висок")) {
            text.push("Не використовуйте воду без фільтрації.");
            text.push("Уникайте пиття сирої води.");
        } else if (risk.includes("серед")) {
            text.push("Використовуйте побутовий фільтр.");
        } else {
            text.push("Якість води є задовільною.");
        }

        if (data.ph < 6.5 || data.ph > 8.5)
            text.push("⚠ Показник pH виходить за межі норми.");
        if (data.nitrates > 50)
            text.push("⚠ Високий рівень нітратів — небезпечно для здоров'я.");
    }

    // ---- SOIL ----
    if (type === "soil") {
        if (risk.includes("висок")) {
            text.push("Уникайте контакту з ґрунтом.");
            text.push("Не вирощуйте рослини на цій території.");
        } else if (risk.includes("серед")) {
            text.push("Контрольне тестування ґрунту рекомендовано.");
        } else {
            text.push("Ґрунт у безпечних межах.");
        }

        if (data.heavy_metals > 300)
            text.push("⚠ Висока концентрація важких металів.");
        if (data.pesticides > 100)
            text.push("⚠ Пестициди на небезпечному рівні.");
    }

    // ---- RADIATION ----
    if (type === "radiation") {
        if (risk.includes("висок")) {
            text.push("Уникайте перебування на відкритому повітрі.");
            text.push("Тримайтеся подалі від джерел випромінювання.");
        } else if (risk.includes("серед")) {
            text.push("Зменшіть час перебування на вулиці.");
        } else {
            text.push("Радіаційний фон у межах норми.");
        }

        if (data.ambient_dose_rate > 2.0)
            text.push("⚠ Високий рівень радіації! Потрібні заходи безпеки.");
    }

    return text;
}

document.addEventListener("DOMContentLoaded", function () {
    const mapElement = document.getElementById("map");
    if (!mapElement) return;

    // --------------------------------
    // 1. Карта
    // --------------------------------
    const map = L.map("map").setView([50.45, 30.52], 5);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19
    }).addTo(map);

    const layers = {
        air: L.layerGroup(),
        water: L.layerGroup(),
        soil: L.layerGroup(),
        radiation: L.layerGroup()
    };
    layers.air.addTo(map);

    // --------------------------------
    // 2. Назви параметрів
    // --------------------------------
    const PARAM_TITLES = {
        air: {
            pm25: "PM2.5",
            pm10: "PM10",
            co: "CO",
            no2: "NO₂",
            o3: "O₃",
            risk_label: "Ризик"
        },
        water: {
            ph: "pH",
            nitrates: "Нітрати",
            conductivity: "Провідність",
            risk_label: "Ризик"
        },
        soil: {
            heavy_metals: "Важкі метали",
            pesticides: "Пестициди",
            ph: "pH",
            risk_label: "Ризик"
        },
        radiation: {
            gamma: "Gamma",
            beta: "Beta",
            alpha: "Alpha",
            ambient_dose_rate: "Амб. доза",
            risk_label: "Ризик"
        }
    };

    // --------------------------------
    // 3. Глобальні змінні для графіка
    // --------------------------------
    let historyChart = null;
    let chartMode = "history";      // "history" | "forecast"
    let currentSelection = null;    // { type, id, data }

    // --------------------------------
    // 4. Завантаження станцій
    // --------------------------------
    fetch("/api/global/")
        .then(res => res.json())
        .then(data => {
            renderMarkers(data.air, layers.air, "air");
            renderMarkers(data.water, layers.water, "water");
            renderMarkers(data.soil, layers.soil, "soil");
            renderMarkers(data.radiation, layers.radiation, "radiation");
        })
        .catch(err => console.error("Помилка /api/global/:", err));

    // POPUP
    function formatPopup(st, type) {
        let html = `<b>${st.name}</b><br>`;
        for (let key in PARAM_TITLES[type]) {
            if (st[key] !== undefined) {
                html += `${PARAM_TITLES[type][key]}: ${st[key]}<br>`;
            }
        }
        html += `<small>${st.timestamp}</small>`;
        return html;
    }

    // Маркери
    function renderMarkers(data, layer, type) {
        layer.clearLayers();

        data.forEach(st => {
            const marker = L.marker(
                [st.lat, st.lon],
                { icon: makeRiskMarker(getColorByRisk(st.risk_label)) }
            );

            marker.bindPopup(formatPopup(st, type));

            marker.on("click", () => {
                currentSelection = { type: type, id: st.id, data: st };
                updateDetailsPanel(st, type);
                loadChart(type, st.id);
            });

            layer.addLayer(marker);
        });
    }

    // --------------------------------
    // 5. Завантаження графіка (Історія / Прогноз)
    // --------------------------------
    function loadChart(type, stationId) {
        const endpoint = chartMode === "forecast"
            ? `/api/forecast/${type}/${stationId}/`
            : `/api/history/${type}/${stationId}/`;

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

                if (historyChart) {
                    historyChart.destroy();
                }

                const labelName =
                    (PARAM_TITLES[type] && PARAM_TITLES[type][param]) ||
                    param.toUpperCase();

                historyChart = new Chart(ctx, {
                    type: "line",
                    data: {
                        labels: labels,
                        datasets: [{
                            label: labelName,
                            data: values,
                            borderWidth: 2,
                            tension: 0.25
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            x: { ticks: { maxTicksLimit: 6 } }
                        }
                    }
                });
            })
            .catch(err => console.error("Помилка завантаження графіка:", err));
    }

    // Навішуємо обробники на кнопки режиму графіка
    function attachChartModeHandlers() {
        const buttons = document.querySelectorAll("#chart-mode button");
        if (!buttons.length) return;

        buttons.forEach(btn => {
            btn.addEventListener("click", function () {
                const mode = this.dataset.mode;
                if (chartMode === mode) return;

                chartMode = mode;

                buttons.forEach(b => {
                    b.classList.remove("btn-primary", "active");
                    b.classList.add("btn-outline-primary");
                });

                this.classList.remove("btn-outline-primary");
                this.classList.add("btn-primary", "active");

                if (currentSelection) {
                    loadChart(currentSelection.type, currentSelection.id);
                }
            });
        });
    }

    // --------------------------------
    // 6. Панель станції справа
    // --------------------------------
    function updateDetailsPanel(st, type) {
        const box = document.getElementById("station-details");
        if (!box) return;

        let html = `<h5 class="fw-bold">${st.name}</h5><ul>`;

        for (let key in PARAM_TITLES[type]) {
            if (st[key] !== undefined) {
                if (key === "risk_label") {
                    const color = getColorByRisk(st[key]);
                    html += `<li><b>${PARAM_TITLES[type][key]}:</b> 
                        <span style="padding:4px 8px; border-radius:6px; background:${color}; color:white;">
                        ${st[key]}</span></li>`;
                } else {
                    html += `<li><b>${PARAM_TITLES[type][key]}:</b> ${st[key]}</li>`;
                }
            }
        }
        html += `</ul>`;

        // Рекомендації
        const adv = getAdvice(type, st);
        if (adv.length) {
            html += `<h6 class="mt-3">Рекомендації</h6><ul>`;
            adv.forEach(a => {
                html += `<li>${a}</li>`;
            });
            html += `</ul>`;
        }

        // Блок графіка + кнопки режиму
        html += `
            <h6 class="mt-3">Динаміка показників</h6>
            <div class="btn-group btn-group-sm mb-2" id="chart-mode">
                <button type="button"
                        class="btn ${chartMode === "history" ? "btn-primary active" : "btn-outline-primary"}"
                        data-mode="history">
                    Історія
                </button>
                <button type="button"
                        class="btn ${chartMode === "forecast" ? "btn-primary active" : "btn-outline-primary"}"
                        data-mode="forecast">
                    Прогноз
                </button>
            </div>
            <div id="chart-container">
                <canvas id="historyChart" height="180"></canvas>
            </div>
        `;

        box.innerHTML = html;

        // Після того як HTML вставлено — чіпляємо обробники кнопок
        attachChartModeHandlers();
    }

    // --------------------------------
    // 7. Перемикання шарів карти
    // --------------------------------
    document.querySelectorAll("input[name='layer']").forEach(radio => {
        radio.addEventListener("change", function () {
            Object.values(layers).forEach(l => map.removeLayer(l));
            layers[this.value].addTo(map);
        });
    });

});
