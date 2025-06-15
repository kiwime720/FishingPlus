document.addEventListener("DOMContentLoaded", () => {
    // 1) 날짜/시간 업데이트
    function updateDateTime() {
      const now = new Date();
      const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
        hour:'2-digit', minute:'2-digit' };
      document.getElementById('dateTime').textContent    = now.toLocaleString('ko-KR', options);
      document.getElementById('dateTime-2').textContent  = now.toLocaleString('ko-KR', options);
    }
    updateDateTime();
    setInterval(updateDateTime, 60000);

    // 2) 지도 초기화
    const map = L.map("map", { scrollWheelZoom: true }).setView([36.5,127.8],7);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap contributors"
    }).addTo(map);

    // 3) 필터 상태 변수
    let currentType   = document.querySelector('.mode-btn.active').dataset.type;
    let currentRegion = document.getElementById('regionSelect').value;

    // 유형 토글 이벤트
    document.querySelectorAll('.mode-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentType = btn.dataset.type;
        updateMarkers();
      });
    });

    // 지역 필터 select 이벤트
    document.getElementById('regionSelect').addEventListener('change', e => {
      currentRegion = e.target.value;
      updateMarkers();
    });

    // 마커 데이터 저장용 배열
    const markersData = [];

    // 4) 낚시터 데이터 로드 및 마커 생성
    fetch('/api/spots')
      .then(res => res.json())
      .then(spots => {
        spots.forEach(s => {
          const regionName = s.road_address.split(' ')[0];
          const marker = L.marker(s.coords);
          marker.on('click', () => {
            document.getElementById('infoContent').innerHTML =
              `<strong>낚시터명:</strong> ${s.name}<br/>` +
              `<strong>낚시터유형:</strong> ${s.type}<br/>` +
              `<strong>도로명주소:</strong> ${s.road_address}`;
            document.getElementById('infoWindow').classList.remove('hidden');
          });
          markersData.push({ spot: s, marker, region: regionName });
        });
        map.on('zoomend', updateMarkers);
        updateMarkers();
      });

    // 5) 필터에 따른 마커 표시/제거
    function updateMarkers() {
      const zoomOk = map.getZoom() >= 3;
      markersData.forEach(({ spot, marker, region }) => {
        const matchType = (spot.type === currentType) || (currentType === '평지' && (spot.type === '기타' || spot.type === '계곡'));
        const matchRegion = (currentRegion === '전체') || (region === currentRegion);
        if (zoomOk && matchType && matchRegion) {
          if (!map.hasLayer(marker)) map.addLayer(marker);
        } else {
          if (map.hasLayer(marker)) map.removeLayer(marker);
        }
      });
    }

    // 6) infoWindow 닫기
    document.getElementById('infoClose').addEventListener('click', () => {
      document.getElementById('infoWindow').classList.add('hidden');
    });

  // 7) 날씨 위젯 채우기
  function fillWeather(containerId, endpoint) {
    fetch(endpoint)
      .then(res => res.json())
      .then(w => {
        const c = document.getElementById(containerId);
        c.querySelector('.weather-icon-main').textContent = {
          '맑음':'☀️','구름조금':'⛅','흐림':'☁️','비':'🌧️'
        }[w.description] || '❓';
        c.querySelector(`#${containerId} #temperature`).textContent = w.temperature + '°C';
        c.querySelector(`#${containerId} #location`).textContent    = w.location;
        c.querySelector(`#${containerId} #sunriseTime`).textContent  = w.sunrise;
        c.querySelector(`#${containerId} #sunsetTime`).textContent   = w.sunset;
        c.querySelector(`#${containerId} #dayLength`).textContent    = w.day_length;
        c.querySelector(`#${containerId} #precipitationChance`).textContent =
          w.description === '비' ? `Rain ${w.precipitation_chance}%` : `${w.description} ${w.precipitation_chance}%`;
        c.querySelector(`#${containerId} #humidity`).textContent  = `Humidity: ${w.humidity}%`;
        c.querySelector(`#${containerId} #windSpeed`).textContent = `Wind: ${w.wind_speed} km/h`;
        const fc = c.querySelector('.forecast');
        fc.innerHTML = '';
        w.forecast.forEach(f => {
          const card = document.createElement('div');
          card.className = 'forecast-card text-center';
          card.innerHTML = `<div class="day">${f.day}</div><div>${f.icon}</div><div>${f.temp}°C</div>`;
          fc.append(card);
        });
      });
  }
  fillWeather('cloud-container', '/api/weather/today');
  fillWeather('cloud-container-2','/api/weather/tomorrow');

  // 8) 물고기 정보 채우기
  fetch('/api/fish')
    .then(res => res.json())
    .then(list => {
      const container = document.querySelector('.info-box h2').parentElement;
      const row = document.createElement('div');
      row.className = 'flex gap-4 mt-2';
      list.forEach(f => {
        const img = document.createElement('img');
        img.src = `https://via.placeholder.com/100?text=${encodeURIComponent(f.species)}`;
        img.alt = f.species;
        img.className = 'rounded-md';
        const lbl = document.createElement('div');
        lbl.textContent = `${f.species} ${f.percent}%`;
        row.append(img, lbl);
      });
      container.append(row);
    });
});
