// static/js/home.js

document.addEventListener('DOMContentLoaded', () => {
  console.log('▶ home.js 시작');

  // 1) DOM 요소 참조
  const title            = document.querySelector('.gmaps-title');
  const menuBtn          = document.querySelector('.gmaps-menu');
  const menuPanel        = document.getElementById('menuPanel');
  const menuClose        = document.getElementById('menuClose');
  const sidePanel        = document.getElementById('sidePanel');
  const sideClose        = document.getElementById('sideClose');
  const sideContent      = document.getElementById('sideContent');
  const loginBtn         = document.getElementById('loginBtn');
  const modalOverlay     = document.getElementById('modalOverlay');
  const cancelBtn        = document.getElementById('cancelBtn');
  const confirmBtn       = document.getElementById('confirmBtn');
  const signupBtn        = document.getElementById('signupBtn');
  const searchInput      = document.getElementById('mapSearch');
  const searchBtn        = document.querySelector('.gmaps-search button');
  const modeBtns         = document.querySelectorAll('.mode-btn');
  const openFreeBoard    = document.getElementById('openFreeBoard');
  const openFavorites    = document.getElementById('openFavorites');
  const boardModal       = document.getElementById('boardModal');
  const favModal         = document.getElementById('favModal');
  const cancelBoardBtn   = document.getElementById('cancelBoardBtn');
  const registerBoardBtn = document.getElementById('registerBoardBtn');
  const cancelFavBtn     = document.getElementById('cancelFavBtn');
  const registerFavBtn   = document.getElementById('registerFavBtn');

  // 2) 타이틀 클릭 → 새로고침
  title?.addEventListener('click', () => window.location.reload());

  // 3) 카카오 맵 초기화
  if (!window.kakao || !kakao.maps) {
    console.error('❌ Kakao Maps SDK 로드 실패');
    return;
  }
  const map = new kakao.maps.Map(
    document.getElementById('map'),
    { center: new kakao.maps.LatLng(36.5, 127.8), level: 13 }
  );

  // 맵 리사이즈 시에도 전체화면 유지
  (function keepMapFullScreen() {
    window.addEventListener('resize', () => {
      const center = map.getCenter();
      map.relayout();
      map.setCenter(center);
    });
  })();

  const clusterer = new kakao.maps.MarkerClusterer({
    map,
    averageCenter: true,
    minLevel: 5
  });

  const redIcon = new kakao.maps.MarkerImage(
    'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/marker_red.png',
    new kakao.maps.Size(27, 40)
  );

  // 4) Spots 로드 & 마커 생성
  let allMarkers = [];
  fetch('/api/spots')
    .then(res => res.json())
    .then(spots => {
      allMarkers = spots.map(spot => {
        const pos = new kakao.maps.LatLng(spot.coords[1], spot.coords[0]);
        const marker = new kakao.maps.Marker({
          position: pos,
          image: spot.type === '실내' ? redIcon : undefined
        });

        // 클릭 시 정보 + 날씨 + 물고기 데이터 렌더
        kakao.maps.event.addListener(marker, 'click', () => {
          map.setCenter(pos);
          map.setLevel(6);

          // 정보 카드 + 날씨 + 물고기 틀 삽입
          sideContent.innerHTML = `
            <div class="info-card">
              <img src="${spot.thumbnail}" class="info-img" alt="${spot.name}"/>
              <div class="info-title">${spot.name}</div>
              <div class="info-rating">
                <span class="rating-value">${spot.rating ?? '4.2'}</span>
                <span class="stars">${
                  '★'.repeat(Math.round(spot.rating ?? 4)) +
                  '☆'.repeat(5 - Math.round(spot.rating ?? 4))
                }</span>
                <span class="reviews">(${spot.reviews ?? 13})</span>
              </div>
              <div class="info-type-phone">
                <span>${spot.type}</span>
                <span style="margin-left:auto;">${spot.tel || '정보없음'}</span>
              </div>
              <div class="info-address">
                <i class="fas fa-map-marker-alt"></i>${spot.address}
              </div>
              <button class="save-btn">저장</button>
            </div>

            <div class="flex gap-4 mt-4">
              <div id="weather1" class="info-box flex-1"></div>
              <div id="weather2" class="info-box flex-1"></div>
            </div>

            <div id="fishInfo" class="info-box mt-4">
              <h2 class="text-xl mb-2">물고기 정보</h2>
              <div class="fish-list flex gap-2"></div>
            </div>
          `;

          // 5) 날씨 데이터 채우기
          fillWeather(
            'weather1',
            `/api/weather?lat=${spot.coords[1]}&lng=${spot.coords[0]}&when=today`
          );
          fillWeather(
            'weather2',
            `/api/weather?lat=${spot.coords[1]}&lng=${spot.coords[0]}&when=tomorrow`
          );

          // 6) 물고기 정보 API 호출 & 렌더링
          fetch(`/api/fish?spot_id=${spot.spot_id}`)
            .then(res => res.json())
            .then(list => {
              const container = sideContent.querySelector('#fishInfo .fish-list');
              container.innerHTML = '';
              list.forEach(f => {
                const wrap = document.createElement('div');
                wrap.className = 'text-center';
                wrap.innerHTML = `
                  <img src="https://via.placeholder.com/80?text=${encodeURIComponent(f.species)}"
                       alt="${f.species}" class="rounded-md mb-1"/>
                  <div class="text-sm">${f.species} (${f.percent}%)</div>
                `;
                container.append(wrap);
              });
            });

          // 사이드패널 열기
          sidePanel.classList.add('open');
        });

        return { spot, marker };
      });

      // 초기 필터링
      updateMarkers(document.querySelector('.mode-btn.active').dataset.mode);
    })
    .catch(err => console.error('❌ spots 로드 에러', err));

  // 7) 필터 함수
  function updateMarkers(type) {
    clusterer.clear();
    const list = allMarkers
      .filter(({ spot }) => spot.type === type)
      .map(({ marker }) => marker);
    clusterer.addMarkers(list);
  }

  // 8) 필터 버튼 이벤트
  modeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      modeBtns.forEach(b => b.classList.remove('active'));
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
      kakao.maps.event.trigger(found.marker, 'click');
    } else {
      alert('검색 결과가 없습니다.');
    }
  }
  searchBtn.addEventListener('click', handleSearch);
  searchInput.addEventListener('keypress', e => {
    if (e.key === 'Enter') handleSearch();
  });

  // 10) 사이드패널 닫기
  sideClose.addEventListener('click', () => sidePanel.classList.remove('open'));

  // 11) 햄버거 메뉴 토글
  menuBtn.addEventListener('click', () => menuPanel.classList.toggle('open'));
  menuClose.addEventListener('click', () => menuPanel.classList.remove('open'));

  // 12) 로그인 모달 제어
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
  cancelBtn.addEventListener('click', () => modalOverlay.classList.add('hidden'));
  confirmBtn.addEventListener('click', () => {
    fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: document.getElementById('userId').value,
        pw: document.getElementById('userPw').value
      })
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

  // 13) 회원가입 버튼
  signupBtn.addEventListener('click', () => {
    modalOverlay.classList.add('hidden');
    window.location.href = '/signup';
  });

  // 14) 자유게시판 / 즐겨찾기 모달 제어
  openFreeBoard.addEventListener('click', () => {
    menuPanel.classList.remove('open');
    boardModal.classList.remove('hidden');
  });
  cancelBoardBtn.addEventListener('click', () => boardModal.classList.add('hidden'));
  registerBoardBtn.addEventListener('click', () => {
    alert('자유게시판에 등록되었습니다.');
    boardModal.classList.add('hidden');
  });
  openFavorites.addEventListener('click', () => {
    menuPanel.classList.remove('open');
    favModal.classList.remove('hidden');
  });
  cancelFavBtn.addEventListener('click', () => favModal.classList.add('hidden'));
  registerFavBtn.addEventListener('click', () => {
    alert('즐겨찾기에 등록되었습니다.');
    favModal.classList.add('hidden');
  });

  // 15) 날씨 채우기 함수
  function fillWeather(containerId, endpoint) {
    fetch(endpoint)
      .then(res => res.json())
      .then(w => {
        const c = document.getElementById(containerId);
        // (여기에 기존 weather-widget-container 내부 요소 업데이트 코드 삽입)
        // 예: c.querySelector('.weather-icon-main').textContent = …
        // 전체 마크업 갱신 대신 부분 업데이트로 관리하세요.
      })
      .catch(err => console.error('❌ 날씨 데이터 로드 에러', err));
  }
});
