// ✅ home.js (업데이트 버전) - 사용자 마커 저장 제거 + 날씨 및 어종 정보 지도 아래 표시

import * as THREE from "https://esm.sh/three";
import { OrbitControls } from "https://esm.sh/three/examples/jsm/controls/OrbitControls.js";

document.addEventListener("DOMContentLoaded", () => {
  const map = L.map("map", { scrollWheelZoom: true }).setView([36.5, 127.8], 7);

  // OSM 기본 레이어
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors"
  }).addTo(map);

  // 오버레이 레이어
  const indoorLayer = L.tileLayer("/api/map/indoor/{z}/{x}/{y}.png");
  const boatLayer = L.tileLayer("/api/map/boat/{z}/{x}/{y}.png");
  let currentOverlay = indoorLayer.addTo(map);

  document.querySelectorAll(".mode-btn").forEach(btn => {
    btn.addEventListener("click", function () {
      document.querySelectorAll(".mode-btn").forEach(b => b.classList.remove("active"));
      this.classList.add("active");
      map.removeLayer(currentOverlay);
      currentOverlay = this.dataset.mode === "indoor" ? indoorLayer : boatLayer;
      map.addLayer(currentOverlay);
      map.invalidateSize();
    });
  });

  // ✅ 저장된 마커 불러오기 (처음 로딩 시)
  let markers = [];
  fetch('/api/spots')
    .then(res => res.json())
    .then(spots => {
      markers = spots.map(s => addMarker(s.lat, s.lng, s.name));
    });

  // ✅ 마커 생성 함수 (줌 레벨에 따라 크기 자동 설정)
  function addMarker(lat, lng, name) {
    const zoom = map.getZoom();
    const size = zoom * 2 + 10;
    const icon = L.icon({
      iconUrl: '/images/fish.png',
      iconSize: [size, size]
    });
    const marker = L.marker([lat, lng], { icon }).addTo(map);
    marker.bindPopup(`<strong>${name}</strong>`);

    marker.on("click", () => {
      fetch(`/api/info?lat=${lat}&lon=${lng}`)
        .then(res => res.json())
        .then(info => {
          document.getElementById("infoContent").innerHTML = `
            <strong>수심:</strong> ${info.depth}<br/>
            <strong>수온:</strong> ${info.temp}<br/>
            <strong>어종:</strong> ${info.fish}
          `;
          document.getElementById("infoWindow").classList.remove("hidden");

          // 지도 아래 날씨 및 어종 정보 출력
          const summaryBox = document.getElementById("summaryBox");
          if (summaryBox) {
            summaryBox.innerHTML = `
              <div class="bg-white/20 backdrop-blur-md p-4 rounded-lg shadow-lg text-white">
                <h3 class="text-xl font-semibold mb-2">선택한 포인트 정보</h3>
                <p><strong>위도:</strong> ${lat.toFixed(4)}, <strong>경도:</strong> ${lng.toFixed(4)}</p>
                <p><strong>수심:</strong> ${info.depth}</p>
                <p><strong>수온:</strong> ${info.temp}</p>
                <p><strong>주요 어종:</strong> ${info.fish}</p>
              </div>
            `;
          }
        });
    });

    return marker;
  }

  // ✅ 줌 변경 시 마커 크기 조절
  map.on('zoomend', () => {
    const zoom = map.getZoom();
    markers.forEach(m => map.removeLayer(m));
    fetch('/api/spots')
      .then(res => res.json())
      .then(spots => {
        markers = spots.map(s => addMarker(s.lat, s.lng, s.name));
      });
  });

  // info 창 닫기
  document.getElementById("infoClose").addEventListener("click", () => {
    document.getElementById("infoWindow").classList.add("hidden");
  });

  // 시간 표시
  function updateDateTime() {
    const now = new Date();
    const optsD = { weekday: "long" };
    const optsT = { hour: "2-digit", minute: "2-digit", hour12: false };
    const text = `${now.toLocaleDateString(undefined, optsD)}, ${now.toLocaleTimeString([], optsT)}`;
    document.querySelectorAll(".date-time").forEach(el => el.textContent = text);
  }
  updateDateTime();
  setInterval(updateDateTime, 60000);
});