// js/home.js
import * as THREE from "https://esm.sh/three";
import { OrbitControls } from "https://esm.sh/three/examples/jsm/controls/OrbitControls.js";

document.addEventListener("DOMContentLoaded", () => {
  // 1) 날짜/시간 업데이트
  function updateDateTime() {
    const now = new Date();
    const optsD = { weekday: "long" };
    const optsT = { hour: "2-digit", minute: "2-digit", hour12: false };
    const text = `${now.toLocaleDateString(undefined, optsD)}, ${now.toLocaleTimeString([], optsT)}`;
    document.querySelectorAll(".date-time").forEach(el => el.textContent = text);
  }
  updateDateTime();
  setInterval(updateDateTime, 60000);

  // 2) 지도 초기화 (휠 줌 활성화)
  const map = L.map("map", { scrollWheelZoom: true }).setView([36.5, 127.8], 7);

  // 3) 베이스 레이어 (OSM)
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors"
  }).addTo(map);

  // 4) 실내/선상 오버레이 레이어 정의
  const indoorLayer = L.tileLayer("/api/map/indoor/{z}/{x}/{y}.png");
  const boatLayer  = L.tileLayer("/api/map/boat/{z}/{x}/{y}.png");
  let currentOverlay = indoorLayer.addTo(map);

  // 토글 버튼 이벤트
  document.querySelectorAll(".mode-btn").forEach(btn => {
    btn.addEventListener("click", function() {
      document.querySelectorAll(".mode-btn").forEach(b => b.classList.remove("active"));
      this.classList.add("active");
      map.removeLayer(currentOverlay);
      currentOverlay = this.dataset.mode === "indoor" ? indoorLayer : boatLayer;
      map.addLayer(currentOverlay);
      map.invalidateSize();
    });
  });

  // 5) 미리 지정된 5개 스폿 (처음엔 숨김)
  const spotsData = [
    { coords: [36.52, 127.85], name: "포인트 A" },
    { coords: [36.48, 127.75], name: "포인트 B" },
    { coords: [36.55, 127.95], name: "포인트 C" },
    { coords: [36.45, 127.90], name: "포인트 D" },
    { coords: [36.50, 127.70], name: "포인트 E" }
  ];
  const spotLayerGroup = L.layerGroup(spotsData.map(s =>
    L.marker(s.coords).bindPopup(`<strong>${s.name}</strong>`)
  ));

  map.on("zoomend", () => {
    const z = map.getZoom();
    if (z >= 3) {
      if (!map.hasLayer(spotLayerGroup)) map.addLayer(spotLayerGroup);
    } else {
      if (map.hasLayer(spotLayerGroup)) map.removeLayer(spotLayerGroup);
    }
  });

  // 6) 확대 시마다 랜덤 스폿 생성 및 클릭 시 infoWindow
  let prevZoom = map.getZoom();
  map.on("zoomend", () => {
    const newZoom = map.getZoom();
    if (newZoom > prevZoom) {
      const bounds = map.getBounds();
      const count = Math.floor(Math.random() * 11) + 10; // 10~20개
      for (let i = 0; i < count; i++) {
        const lat = bounds.getSouth() + Math.random() * (bounds.getNorth() - bounds.getSouth());
        const lng = bounds.getWest()  + Math.random() * (bounds.getEast()  - bounds.getWest());
        const marker = L.marker([lat, lng]).addTo(map);

        marker.on("click", () => {
          const depth   = (Math.random() * 30 + 5).toFixed(1) + " m";
          const temp    = (Math.random() * 15 + 10).toFixed(1) + " °C";
          const species = ["광어","참돔","농어","전어","도미"];
          const fish    = species[Math.floor(Math.random() * species.length)];
          document.getElementById("infoContent").innerHTML = `
            <strong>수심:</strong> ${depth}<br/>
            <strong>수온:</strong> ${temp}<br/>
            <strong>어종:</strong> ${fish}
          `;
          document.getElementById("infoWindow").classList.remove("hidden");
        });
      }
    }
    prevZoom = newZoom;
  });

  // 7) infoWindow 닫기
  document.getElementById("infoClose").addEventListener("click", () => {
    document.getElementById("infoWindow").classList.add("hidden");
  });

  // 8) 테스트 마커
  L.marker([36.5, 127.8]).addTo(map).bindPopup("테스트 마커").openPopup();
});
