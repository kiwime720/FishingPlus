// static/js/home.js
document.addEventListener('DOMContentLoaded', () => {
  console.log('▶ home.js 시작');

  // Kakao SDK 확인
  if (!window.kakao || !kakao.maps) {
    console.error('❌ Kakao Maps SDK 로드 실패');
    return;
  }

  // 0) Fishing+ 클릭 시 새로고침
  const title = document.querySelector('.gmaps-title');
  if (title) {
    title.style.cursor = 'pointer';
    title.addEventListener('click', () => {
      window.location.reload();
    });
  }

  // 1) 지도 초기화 (level=9)
  const mapContainer = document.getElementById('map');
  const mapOptions = {
    center: new kakao.maps.LatLng(36.5, 127.8),
    level: 13
  };
  const map = new kakao.maps.Map(mapContainer, mapOptions);
  console.log('🗺 지도 생성 (level=13)');

  // 2) 클러스터러 생성
  const clusterer = new kakao.maps.MarkerClusterer({
    map,
    averageCenter: true,
    minLevel: 5
  });

  // 3) 빨간 마커 아이콘 정의 (실내 낚시용)
  const redSrc   = 'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/marker_red.png';
  const iconSize = new kakao.maps.Size(27, 40);
  const redIcon  = new kakao.maps.MarkerImage(redSrc, iconSize);

  // 4) 사이드 패널 요소
  const sidePanel   = document.getElementById('sidePanel');
  const sideClose   = document.getElementById('sideClose');
  const sideContent = document.getElementById('sideContent');
  sideClose.addEventListener('click', () => {
    sidePanel.classList.remove('open');
  });

  // 5) 검색바 요소
  const searchInput = document.getElementById('mapSearch');
  const searchBtn   = document.querySelector('.gmaps-search button');

  // 6) 스폿 데이터 로드 후 마커 생성
  let allMarkers = [];
  fetch('/api/spots')
    .then(res => res.json())
    .then(spots => {
      console.log('📋 spots 개수:', spots.length);

      allMarkers = spots.map(spot => {
        const lat = spot.coords[1], lng = spot.coords[0];
        const position = new kakao.maps.LatLng(lat, lng);

        // 타입에 따라 아이콘 설정 (indoor = 빨간, boat = 기본 파랑)
        const markerOpts = { position };
        if (spot.type === 'indoor') markerOpts.image = redIcon;

        const marker = new kakao.maps.Marker(markerOpts);

        // 마커 클릭 시 사이드 패널 열기
        kakao.maps.event.addListener(marker, 'click', () => {
          // 지도 중심 이동 및 확대
          map.setCenter(position);
          map.setLevel(6);

          // 정보 표시
          sideContent.innerHTML = `
            <strong>이름:</strong> ${spot.name}<br/>
            <strong>유형:</strong> ${spot.type}<br/>
            <strong>주소:</strong> ${spot.address}<br/>
            <strong>전화:</strong> ${spot.tel || '정보없음'}<br/>
            <strong>운영시간:</strong> ${spot.operation_hours || '정보없음'}
          `;
          sidePanel.classList.add('open');
        });

        return { spot, marker };
      });

      // 초기 필터링
      const initMode = document.querySelector('.mode-btn.active').dataset.mode;
      updateMarkers(initMode);
    })
    .catch(err => console.error('❌ spots 로드 에러', err));

  // 7) 마커 필터링 함수
  function updateMarkers(filterType) {
    clusterer.clear();
    const list = allMarkers
      .filter(({ spot }) => spot.type === filterType)
      .map(({ marker }) => marker);
    clusterer.addMarkers(list);
  }

  // 8) 필터 버튼 이벤트
  document.querySelectorAll('.mode-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      sidePanel.classList.remove('open');
      updateMarkers(btn.dataset.mode);
    });
  });

  // 9) 검색 기능
  function handleSearch() {
    const term = searchInput.value.trim().toLowerCase();
    if (!term) return;
    const found = allMarkers.find(({ spot }) =>
      spot.name.toLowerCase().includes(term)
    );
    if (found) {
      const { spot, marker } = found;
      const pos = marker.getPosition();
      map.setCenter(pos);
      map.setLevel(6);
      sideContent.innerHTML = `
        <strong>이름:</strong> ${spot.name}<br/>
        <strong>유형:</strong> ${spot.type}<br/>
        <strong>주소:</strong> ${spot.address}<br/>
        <strong>전화:</strong> ${spot.tel || '정보없음'}<br/>
        <strong>운영시간:</strong> ${spot.operation_hours || '정보없음'}
      `;
      sidePanel.classList.add('open');
    } else {
      alert('검색 결과가 없습니다.');
    }
  }

  searchBtn.addEventListener('click', handleSearch);
  searchInput.addEventListener('keypress', e => {
    if (e.key === 'Enter') handleSearch();
  });

  // 10) 로그인 / 로그아웃 제어
  const loginBtn     = document.getElementById('loginBtn');
  const modalOverlay = document.getElementById('modalOverlay');
  const cancelBtn    = document.getElementById('cancelBtn');
  const confirmBtn   = document.getElementById('confirmBtn');

  loginBtn.addEventListener('click', () => {
    if (loginBtn.dataset.loggedIn === 'true') {
      fetch('/api/logout', { method: 'POST' })
        .then(() => {
          loginBtn.textContent = '로그인';
          delete loginBtn.dataset.loggedIn;
        })
        .catch(() => alert('로그아웃 중 오류가 발생했습니다.'));
    } else {
      modalOverlay.classList.remove('hidden');
    }
  });

  cancelBtn.addEventListener('click', () => {
    modalOverlay.classList.add('hidden');
  });

  confirmBtn.addEventListener('click', () => {
    const id = document.getElementById('userId').value;
    const pw = document.getElementById('userPw').value;
    fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, pw })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          modalOverlay.classList.add('hidden');
          loginBtn.textContent = '로그아웃';
          loginBtn.dataset.loggedIn = 'true';
        } else {
          alert(`로그인 실패: ${data.message}`);
        }
      })
      .catch(() => alert('로그인 중 서버 통신 오류'));
  });
});
