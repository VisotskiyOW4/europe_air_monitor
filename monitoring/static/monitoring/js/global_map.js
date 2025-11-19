// ===============================
// === Генерація кольору по ризику ===
// ===============================
function getColorByRisk(risk) {
    if (!risk) return "#999";

    const r = risk.toLowerCase();
    if (r.includes("низь") || r.includes("low")) return "#2ecc71";    // зелений
    if (r.includes("серед") || r.includes("medium")) return "#f1c40f"; // жовтий
    if (r.includes("висок") || r.includes("high")) return "#e74c3c";   // червоний
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

function getAdvice(type, data) {
    let risk = data.risk_label.toLowerCase();
    let text = [];

    // ------------------------
    // AIR
    // ------------------------
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

    // ------------------------
    // WATER
    // ------------------------
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

    // ------------------------
    // SOIL
    // ------------------------
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

    // ------------------------
    // RADIATION
    // ------------------------
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

    // ============================
    // === 1. Карта
    // ============================
    const map = L.map("map").setView([50.45, 30.52], 5);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19
    }).addTo(map);

    // Групи маркерів
    const layers = {
        air: L.layerGroup(),
        water: L.layerGroup(),
        soil: L.layerGroup(),
        radiation: L.layerGroup()
    };
    layers.air.addTo(map);

    // ============================
    // === 2. Назви параметрів
    // ============================
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

    // ============================
    // === 3. Завантаження API
    // ============================
    fetch("/api/global/")
        .then(res => res.json())
        .then(data => {
            renderMarkers(data.air, layers.air, "air");
            renderMarkers(data.water, layers.water, "water");
            renderMarkers(data.soil, layers.soil, "soil");
            renderMarkers(data.radiation, layers.radiation, "radiation");
        });

    // ============================
    // === 4. POPUP
    // ============================
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

    // ============================
    // === 5. Маркери
    // ============================
    function renderMarkers(data, layer, type) {
        layer.clearLayers();

        data.forEach(st => {
            const marker = L.marker(
                [st.lat, st.lon],
                { icon: makeRiskMarker(getColorByRisk(st.risk_label)) }
            );

            marker.bindPopup(formatPopup(st, type));

            marker.on("click", () => {
                updateDetailsPanel(st, type);
                loadHistoryChart(type, st.id);
            });

            layer.addLayer(marker);
        });
    }

    // ============================
    // === 6. Графік (Chart.js)
    // ============================
    let historyChart = null;

    function loadHistoryChart(type, stationId) {
        fetch(`/api/history/${type}/${stationId}/`)
            .then(r => r.json())
            .then(data => {
                if (!data.timestamps || !data.values) return;

                const ctx = document.getElementById("historyChart").getContext("2d");
                if (historyChart) historyChart.destroy();

                historyChart = new Chart(ctx, {
                    type: "line",
                    data: {
                        labels: data.timestamps,
                        datasets: [{
                            label: PARAM_TITLES[type][data.param] || data.param,
                            data: data.values,
                            borderWidth: 2,
                            borderColor: "#3498db",
                            pointRadius: 3,
                            tension: 0.3
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            x: { ticks: { maxRotation: 90, minRotation: 45 } },
                            y: { beginAtZero: true }
                        }
                    }
                });
            });
    }



    // ============================
    // === 7. Панель станції
    // ============================
    function updateDetailsPanel(st, type) {
        const box = document.getElementById("station-details");

        let html = `<h4>${st.name}</h4><ul>`;

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

        // === Рекомендації ===
        const advices = getAdvice(type, st);
        html += `<h5 class="mt-3">Рекомендації</h5><ul>`;
        advices.forEach(a => html += `<li>${a}</li>`);
        html += `</ul>`;

        // === Блок графіка ===
        html += `
            <h5 class="mt-3">Динаміка показників</h5>
            <div id="chart-container">
                <canvas id="historyChart" height="200"></canvas>
            </div>
        `;

        box.innerHTML = html;
    }



    // ============================
    // === 8. Перемикання шарів
    // ============================
    document.querySelectorAll("input[name='layer']").forEach(radio => {
        radio.addEventListener("change", function () {
            Object.values(layers).forEach(l => map.removeLayer(l));
            layers[this.value].addTo(map);
        });
    });

});
