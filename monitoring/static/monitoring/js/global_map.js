// ===============================
// === Генерація кольорових маркерів ===
// ===============================

// Повертає колір на основі fuzzy-ризику
function getColorByRisk(risk) {
    if (!risk) return "#999";

    const r = risk.toLowerCase();
    if (r.includes("low") || r.includes("низь")) return "#2ECC71";
    if (r.includes("medium") || r.includes("серед")) return "#F1C40F";
    if (r.includes("high") || r.includes("висок")) return "#E74C3C";

    return "#999";
}

// Створення круглого маркера
function makeRiskMarker(color) {
    return L.divIcon({
        className: "custom-marker",
        html: `<div style="
            width: 18px;
            height: 18px;
            background: ${color};
            border: 2px solid #fff;
            border-radius: 50%;
            box-shadow: 0 0 5px #333;
        "></div>`,
        iconSize: [18, 18],
        iconAnchor: [9, 9]
    });
}


document.addEventListener("DOMContentLoaded", function () {

    const mapElement = document.getElementById("map");
    if (!mapElement) return;

    // === Створення карти ===
    const map = L.map("map").setView([50.45, 30.52], 5);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // === Групи шарів ===
    const layers = {
        air: L.layerGroup(),
        water: L.layerGroup(),
        soil: L.layerGroup(),
        radiation: L.layerGroup()
    };

    layers.air.addTo(map);

    // === Завантаження загального API ===
    fetch("/api/global/")
        .then(r => r.json())
        .then(data => {
            console.log("Global API:", data);

            renderMarkers(data.air, layers.air, "air");
            renderMarkers(data.water, layers.water, "water");
            renderMarkers(data.soil, layers.soil, "soil");
            renderMarkers(data.radiation, layers.radiation, "radiation");
        });


    // === Заголовки параметрів ===
    const PARAM_TITLES = {
        air: {
            pm25: "PM2.5",
            pm10: "PM10",
            co: "CO",
            no2: "NO₂",
            o3: "O₃",
            risk_label: "Ризик",
        },
        water: {
            ph: "pH",
            nitrates: "Нітрати",
            conductivity: "Провідність",
            risk_label: "Ризик",
        },
        soil: {
            heavy_metals: "Важкі метали",
            pesticides: "Пестициди",
            ph: "pH",
            risk_label: "Ризик",
        },
        radiation: {
            gamma: "Gamma",
            beta: "Beta",
            alpha: "Alpha",
            ambient_dose_rate: "Ambient dose rate",
            risk_label: "Ризик",
        }
    };


    // ===============================
    // === Рендер маркерів ===
    // ===============================
    function renderMarkers(stations, layerGroup, type) {
        layerGroup.clearLayers();

        stations.forEach(st => {

            const color = getColorByRisk(st.risk_label);

            const marker = L.marker(
                [st.lat, st.lon],
                { icon: makeRiskMarker(color) }
            );

            marker.bindPopup(formatStation(st, type));

            marker.on("click", () => {
                updateDetailsPanel(st, type);
            });

            layerGroup.addLayer(marker);
        });
    }


    // ===============================
    // === Popup форматування ===
    // ===============================
    function formatStation(st, type) {
        let html = `<b>${st.name}</b><br>`;

        for (let key in PARAM_TITLES[type]) {
            if (st[key] !== undefined) {
                html += `${PARAM_TITLES[type][key]}: ${st[key]}<br>`;
            }
        }
        html += `<small>${st.timestamp}</small>`;
        return html;
    }


    // ===============================
    // === Графік історії ===
    // ===============================
    let historyChart = null;

    function loadHistoryChart(type, station_id) {

        fetch(`/api/history/${type}/${station_id}/`)
            .then(r => r.json())
            .then(data => {

                const ctx = document.getElementById("historyChart").getContext("2d");

                if (historyChart) historyChart.destroy();

                historyChart = new Chart(ctx, {
                    type: "line",
                    data: {
                        labels: data.timestamps,
                        datasets: [{
                            label: data.param,
                            data: data.values,
                            borderColor: "#007BFF",
                            borderWidth: 2,
                            fill: false
                        }]
                    },
                    options: { responsive: true }
                });
            });
    }


    // ===============================
    // === Панель справа ===
    // ===============================
    function updateDetailsPanel(st, type) {
        const box = document.getElementById("station-details");

        let html = `<h4>${st.name}</h4><ul>`;

        for (let key in PARAM_TITLES[type]) {
            if (st[key] !== undefined) {
                html += `<li><b>${PARAM_TITLES[type][key]}:</b> ${st[key]}</li>`;
            }
        }

        html += `</ul>
            <h5>Динаміка показників</h5>
            <canvas id="historyChart" height="140"></canvas>
        `;

        box.innerHTML = html;

        //Завантажуємо історію за ID
        loadHistoryChart(type, st.id);
    }


    // ===============================
    // === Перемикачі шарів ===
    // ===============================
    document.querySelectorAll("input[name='layer']").forEach(radio => {
        radio.addEventListener("change", function () {
            Object.values(layers).forEach(l => map.removeLayer(l));
            layers[this.value].addTo(map);
        });
    });

});
