// js/home.js
import * as THREE from "https://esm.sh/three";
import { OrbitControls } from "https://esm.sh/three/examples/jsm/controls/OrbitControls.js";

document.addEventListener('DOMContentLoaded', () => {
  // 1) 날짜/시간 업데이트 및 Three.js 3D 구름 애니메이션
  const dateTimeEl = document.getElementById('dateTime');
  function updateDateTime() {
    const now = new Date();
    const optsD = { weekday: 'long' }, optsT = { hour:'2-digit', minute:'2-digit', hour12:false };
    dateTimeEl.textContent = `${now.toLocaleDateString(undefined, optsD)}, ${now.toLocaleTimeString([], optsT)}`;
  }
  updateDateTime();
  setInterval(updateDateTime, 60000);

  // Three.js cloud animation logic … (생략 가능)
  // …

  // 2) Leaflet 지도 초기화 및 검색 필터 적용
  const map = L.map('map').setView([36.5, 127.8], 7);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  const locations = [
    { name: '참돔', coords: [35.9, 128.6] },
    { name: '광어', coords: [34.8, 128.6] },
    { name: '농어', coords: [37.5, 126.9] },
    { name: '전어', coords: [36.4, 127.4] }
  ];
  const markers = locations.map(loc =>
    L.marker(loc.coords).bindPopup(`<strong>${loc.name}</strong> 낚시 포인트`).addTo(map)
  );

  document.getElementById('mapSearch').addEventListener('input', e => {
    const q = e.target.value.trim().toLowerCase();
    markers.forEach(m => {
      const name = m.getPopup().getContent().toLowerCase();
      q && !name.includes(q) ? map.removeLayer(m) : map.addLayer(m);
    });
  });
});