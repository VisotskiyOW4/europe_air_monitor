// === Генерація кольорових маркерів (Leaflet divIcon) ===
function makeMarker(color) {
    return L.divIcon({
        className: "custom-marker",
        html: `<div style="
            width: 16px;
            height: 16px;
            background: ${color};
            border: 2px solid white;
            border-radius: 50%;
            box-shadow: 0 0 4px #333;
        "></div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    });
}

// Кольори маркерів для кожного типу моніторингу
const markerStyles = {
    air: "#1E90FF",       // синій
    water: "#00BFFF",     // бірюзовий
    soil: "#8B4513",      // коричневий
    radiation: "#FF4500"  // яскраво-помаранчевий
};



document.addEventListener("DOMContentLoaded", function () {

    const mapElement = document.getElementById("map");
    if (!mapElement) return;

    // === 1. Створення карти ===
    const map = L.map("map").setView([50.45, 30.52], 5);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // === 2. Групи маркерів ===
    const layers = {
        air: L.layerGroup(),
        water: L.layerGroup(),
        soil: L.layerGroup(),
        radiation: L.layerGroup()
    };

    layers.air.addTo(map); // стартовий шар

    // === 3. Завантаження усіх станцій ===
    fetch("/api/global/")
        .then(response => response.json())
        .then(data => {
            console.log("Global API:", data);

            renderMarkers(data.air, layers.air, "air");
            renderMarkers(data.water, layers.water, "water");
            renderMarkers(data.soil, layers.soil, "soil");
            renderMarkers(data.radiation, layers.radiation, "radiation");
        })
        .catch(err => console.error("Помилка API:", err));

    // === 4. Заголовки параметрів ===
    const PARAM_TITLES = {
    air: {
        pm25: "PM2.5",
        pm10: "PM10",
        co: "CO",
        no2: "NO₂",
        o3: "O₃",
        risk_label: "Ризик",          // ← додали
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

    // === 5. Форматування popup ===
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

    // === 6. Рендер маркерів ===
    function renderMarkers(stations, layerGroup, type) {
        layerGroup.clearLayers();

        stations.forEach(st => {
            const marker = L.marker(
                [st.lat, st.lon],
                { icon: makeMarker(markerStyles[type]) }
            );

            marker.bindPopup(formatStation(st, type));

            marker.on("click", () => {
                updateDetailsPanel(st, type);
            });

            layerGroup.addLayer(marker);
        });
    }

    // === 7. Панель справа ===
    function updateDetailsPanel(st, type) {
        const box = document.getElementById("station-details");
        if (!box) return;

        let html = `<h4>${st.name}</h4><ul>`;

        for (let key in PARAM_TITLES[type]) {
            if (st[key] !== undefined) {
                html += `<li><b>${PARAM_TITLES[type][key]}:</b> ${st[key]}</li>`;
            }
        }

        html += `</ul><small>${st.timestamp}</small>`;
        box.innerHTML = html;
    }

    // === 8. Перемикання шарів ===
    document.querySelectorAll("input[name='layer']").forEach(radio => {
        radio.addEventListener("change", function () {
            Object.values(layers).forEach(l => map.removeLayer(l));
            layers[this.value].addTo(map);
        });
    });

});
