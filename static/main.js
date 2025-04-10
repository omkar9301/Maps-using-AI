const map = L.map('map').setView([19.0760, 72.8777], 14);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

let control;

function route() {
  const start = document.getElementById("start").value;
  const end = document.getElementById("end").value;

  if (control) {
    map.removeControl(control);
  }

  control = L.Routing.control({
    waypoints: [
      L.latLng(...start.split(",")),
      L.latLng(...end.split(","))
    ],
    routeWhileDragging: false
  }).addTo(map);

  control.on('routesfound', function(e) {
    const route = e.routes[0];
    const routeCoords = route.coordinates;

    fetch('/api/hazards')
      .then(res => res.json())
      .then(hazards => {
        hazards.forEach(hazard => {
          routeCoords.forEach(coord => {
            const dist = getDistance(coord.lat, coord.lng, hazard.lat, hazard.lng);
            if (dist < 100) {
              L.marker([hazard.lat, hazard.lng])
                .bindPopup(`Hazard: ${hazard.type}`)
                .addTo(map);
            }
          });
        });
      });
  });
}

function getDistance(lat1, lon1, lat2, lon2) {
  const R = 6371e3;
  const φ1 = lat1 * Math.PI/180, φ2 = lat2 * Math.PI/180;
  const Δφ = (lat2-lat1) * Math.PI/180;
  const Δλ = (lon2-lon1) * Math.PI/180;

  const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
            Math.cos(φ1) * Math.cos(φ2) *
            Math.sin(Δλ/2) * Math.sin(Δλ/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}