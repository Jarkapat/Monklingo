{% extends 'base/base.html' %}
{% load static %}
{% block main %}

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>

<!-- Leaflet Routing Machine -->
<link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.css" />
<script src="https://unpkg.com/leaflet-routing-machine/dist/leaflet-routing-machine.js"></script>

<style>
    .map-container {
        width: 100%;
        height: 500px;
        margin-bottom: 30px;
        border: 1px solid #ddd;
    }
</style>

<div class="flex-1 overflow-y-auto ml-[300px] mt-10">
    <h1>จัดการเส้นทางบิณฑบาต</h1>

    <!-- แสดงแผนที่ -->
    <div id="map" class="map-container"></div>

    <!-- รายการเส้นทาง -->
    <h2>เลือกเส้นทาง</h2>
    <select id="route_select" onchange="loadCheckpoints()">
        <option value="">เลือกเส้นทาง</option>
    </select>
</div>

<script>
    let map, movingMarker, routeControl;
    let checkpointMarkers = [];

    window.onload = function() {
        console.log("✅ Window fully loaded, initializing map...");
        initMap();
        fetchRoutes();
    };

    function initMap() {
        map = L.map("map").setView([13.736717, 100.523186], 13);
        
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        movingMarker = L.marker([13.736717, 100.523186], {
            icon: L.icon({
                iconUrl: "https://cdn-icons-png.flaticon.com/512/3448/3448577.png", 
                iconSize: [40, 40]
            })
        }).addTo(map);

        console.log("✅ Leaflet map initialized!");
    }

    function fetchRoutes() {
        fetch("/api/routes/")
            .then(response => response.json())
            .then(routes => {
                console.log("✅ Fetched routes:", routes);
                let select = document.getElementById("route_select");
                select.innerHTML = `<option value="">เลือกเส้นทาง</option>`;
                routes.forEach(route => {
                    let option = document.createElement("option");
                    option.value = route.id;
                    option.textContent = `${route.name} (เริ่ม ${route.start_time})`;
                    select.appendChild(option);
                });
            })
            .catch(error => console.error("❌ Error fetching routes:", error));
    }

    function loadCheckpoints() {
        let routeId = document.getElementById("route_select").value;
        if (!routeId) return;

        fetch(`/api/routes/${routeId}/checkpoints/`)
            .then(response => response.json())
            .then(checkpoints => {
                console.log("✅ Loaded checkpoints:", checkpoints);
                if (checkpoints.length < 2) {
                    alert("❌ ต้องมีอย่างน้อย 2 จุดเพื่อสร้างเส้นทาง!");
                    return;
                }

                // ลบ Marker เดิมทั้งหมด
                checkpointMarkers.forEach(marker => map.removeLayer(marker));
                checkpointMarkers = [];

                let waypoints = checkpoints.map(cp => {
                    let marker = L.marker([cp.lat, cp.lon], {
                        icon: L.icon({
                            iconUrl: "https://cdn-icons-png.flaticon.com/512/684/684908.png", 
                            iconSize: [30, 30]
                        })
                    }).addTo(map);

                    marker.bindTooltip(cp.name, { permanent: true, direction: "top" }).openTooltip();
                    checkpointMarkers.push(marker);

                    return L.latLng(cp.lat, cp.lon);
                });

                if (routeControl) {
                    map.removeControl(routeControl);
                }

                routeControl = L.Routing.control({
                    waypoints: waypoints,
                    createMarker: function() { return null; },
                    routeWhileDragging: false
                }).addTo(map);

                routeControl.on("routesfound", function (e) {
                    let route = e.routes[0].coordinates;
                    moveMarkerAlongRoute(route, checkpoints);
                });
            })
            .catch(error => console.error("❌ Error loading checkpoints:", error));
    }

    function moveMarkerAlongRoute(routeCoords, checkpoints) {
        let index = 0;
        function moveToNextPoint() {
            if (index >= routeCoords.length - 1) {
                console.log("✅ Marker เดินทางถึงจุดสุดท้ายแล้ว!");
                return;
            }

            let start = routeCoords[index];
            let end = routeCoords[index + 1];

            let duration = (checkpoints[Math.floor(index / (routeCoords.length / checkpoints.length))].travel_time || 5) * 1000 * 60;
            console.log(`🚶 Moving on road section ${index + 1}/${routeCoords.length} in ${duration / 1000} seconds`);

            let startTime = performance.now();
            function animateMarker() {
                let now = performance.now();
                let elapsed = now - startTime;
                let progress = Math.min(elapsed / duration, 1);

                let lat = start.lat + (end.lat - start.lat) * progress;
                let lon = start.lng + (end.lng - start.lng) * progress;
                
                movingMarker.setLatLng([lat, lon]);

                if (progress < 1) {
                    requestAnimationFrame(animateMarker);
                } else {
                    index++;
                    setTimeout(moveToNextPoint, 100);
                }
            }
            requestAnimationFrame(animateMarker);
        }

        moveToNextPoint();
    }
</script>

{% endblock %}
