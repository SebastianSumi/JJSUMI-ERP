(function () {
    const initJjsumiMap = () => {
        const btnLocate = document.getElementById("jjsumi_btn_locate");
        const statusEl = document.getElementById("jjsumi_geo_status");
        const mapEl = document.getElementById("jjsumi_map");
        const rowEl = document.getElementById("jjsumi_branches_row");
        const cards = Array.from(document.querySelectorAll(".jjsumi_branch_card"));

        if (!cards.length || !mapEl || mapEl.dataset.jjsumiInit) {
            return;
        }
        mapEl.dataset.jjsumiInit = "1";

    const toRad = (deg) => (deg * Math.PI) / 180;
    const haversineKm = (lat1, lon1, lat2, lon2) => {
        const R = 6371;
        const dLat = toRad(lat2 - lat1);
        const dLon = toRad(lon2 - lon1);
        const a =
            Math.sin(dLat / 2) ** 2 +
            Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
        return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    };

    let map = null;
    let userMarker = null;
    let routeLine = null;
    const branchMarkers = new Map();

    const makeBranchIcon = (isNearest) =>
        window.L.divIcon({
            className: "jjsumi-pin-wrap",
            html: `<div class="jjsumi-pin ${isNearest ? "is-nearest" : ""}"><span>J</span></div>`,
            iconSize: [36, 44],
            iconAnchor: [18, 44],
            popupAnchor: [0, -40],
        });

    const makeUserIcon = () =>
        window.L.divIcon({
            className: "jjsumi-user-pin-wrap",
            html: `<div class="jjsumi-user-pin"></div>`,
            iconSize: [22, 22],
            iconAnchor: [11, 11],
        });

    const buildPopupHtml = (card, distText = "") => {
        const name = card.dataset.name;
        const addr = card.dataset.address;
        const cardBtn = card.querySelector(".jjsumi_btn_directions");
        const dirUrl = cardBtn
            ? cardBtn.href
            : `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(addr || `${card.dataset.lat},${card.dataset.lng}`)}&travelmode=driving`;
        return `
            <div style="min-width:210px;font-family:inherit;">
                <div style="font-weight:700;color:#101F3A;font-size:14px;">${name}</div>
                <div style="color:#667085;font-size:12px;margin:3px 0 6px;">${addr}</div>
                ${distText ? `<div style="color:#16a34a;font-weight:700;font-size:12px;margin-bottom:8px;">${distText}</div>` : ""}
                <a href="${dirUrl}" target="_blank" rel="noopener"
                   class="btn btn-sm btn-warning fw-semibold"
                   style="color:#101F3A;text-decoration:none;">
                    <i class="fa fa-location-arrow me-1"></i>Cómo llegar
                </a>
            </div>
        `;
    };

    const initMap = () => {
        if (!window.L) {
            setTimeout(initMap, 250);
            return;
        }
        if (map) return;
        map = window.L.map(mapEl, { scrollWheelZoom: false }).setView([-15.85, -70.65], 6);
        window.L.tileLayer("https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", {
            attribution: "&copy; Google Maps · JJSUMI",
            maxZoom: 19,
        }).addTo(map);

        cards.forEach((card, idx) => {
            const lat = parseFloat(card.dataset.lat);
            const lng = parseFloat(card.dataset.lng);
            const marker = window.L.marker([lat, lng], { icon: makeBranchIcon(idx === 0) })
                .addTo(map)
                .bindPopup(buildPopupHtml(card));
            branchMarkers.set(card, marker);
        });
    };

    initMap();

    const focusBranch = (card) => {
        cards.forEach((c) => {
            c.classList.remove("is-nearest");
            const m = branchMarkers.get(c);
            if (m) m.setIcon(makeBranchIcon(false));
        });
        card.classList.add("is-nearest");
        const lat = parseFloat(card.dataset.lat);
        const lng = parseFloat(card.dataset.lng);
        const m = branchMarkers.get(card);
        if (m && map) {
            m.setIcon(makeBranchIcon(true));
            map.setView([lat, lng], 15, { animate: true });
            m.openPopup();
        }
    };

    document.querySelectorAll(".jjsumi_btn_map").forEach((btn) => {
        btn.addEventListener("click", () => {
            const card = btn.closest(".jjsumi_branch_card");
            if (card) focusBranch(card);
        });
    });

    const applyUserLocation = (uLat, uLng, sourceLabel) => {
        const ranked = cards
            .map((card) => {
                const sLat = parseFloat(card.dataset.lat);
                const sLng = parseFloat(card.dataset.lng);
                return { card, sLat, sLng, dist: haversineKm(uLat, uLng, sLat, sLng) };
            })
            .sort((a, b) => a.dist - b.dist);

        ranked.forEach(({ card, dist }, idx) => {
            card.classList.toggle("is-nearest", idx === 0);
            const distText = `${idx === 0 ? "★ Más cercana · " : ""}Aprox. ${dist.toFixed(1)} km de ti`;
            const distEl = card.querySelector(".jjsumi_branch_dist");
            if (distEl) {
                distEl.textContent = distText;
                distEl.classList.remove("d-none");
            }
            const m = branchMarkers.get(card);
            if (m) {
                m.setIcon(makeBranchIcon(idx === 0));
                m.setPopupContent(buildPopupHtml(card, distText));
            }
            if (rowEl && card.parentElement) {
                rowEl.appendChild(card.parentElement);
            }
        });

        const best = ranked[0];
        if (map && best) {
            if (userMarker) map.removeLayer(userMarker);
            if (routeLine) map.removeLayer(routeLine);

            userMarker = window.L.marker([uLat, uLng], { icon: makeUserIcon() })
                .addTo(map)
                .bindPopup("<b>Tu ubicación actual</b>");
            routeLine = window.L.polyline(
                [
                    [uLat, uLng],
                    [best.sLat, best.sLng],
                ],
                { color: "#2563eb", weight: 3, dashArray: "6 6" }
            ).addTo(map);

            const bounds = window.L.latLngBounds([
                [uLat, uLng],
                [best.sLat, best.sLng],
            ]);
            map.fitBounds(bounds, { padding: [55, 55], maxZoom: 15 });
            const bestMarker = branchMarkers.get(best.card);
            if (bestMarker) bestMarker.openPopup();
        }

        if (statusEl && best) {
            statusEl.textContent = `Ubicación detectada (${sourceLabel}). Sucursal más cercana: ${best.card.dataset.name} (${best.dist.toFixed(1)} km).`;
        }
    };

    const fallbackIpLocation = async () => {
        try {
            const resp = await fetch("https://ipwho.is/");
            const data = await resp.json();
            if (data && data.success && typeof data.latitude === "number" && typeof data.longitude === "number") {
                applyUserLocation(data.latitude, data.longitude, data.city || "IP");
                return;
            }
        } catch {
            // Ignorar si no hay red externa
        }
        if (statusEl) {
            statusEl.textContent = "Permite la ubicación en tu navegador o pulsa 'Cómo llegar' en tu sucursal para abrir la ruta en Google Maps.";
        }
    };

        if (btnLocate) {
            btnLocate.addEventListener("click", () => {
                if (statusEl) statusEl.textContent = "Detectando tu ubicación...";
                if (!navigator.geolocation) {
                    void fallbackIpLocation();
                    return;
                }
                navigator.geolocation.getCurrentPosition(
                    (pos) => applyUserLocation(pos.coords.latitude, pos.coords.longitude, "GPS"),
                    () => {
                        void fallbackIpLocation();
                    },
                    { enableHighAccuracy: true, timeout: 6000 }
                );
            });
        }
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initJjsumiMap);
    } else {
        initJjsumiMap();
    }
})();
