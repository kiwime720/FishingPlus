  document.addEventListener('DOMContentLoaded', () => {
    console.log('▶ home.js 시작');

    // 로그인 상태: 새로고침해도 유지
    let currentUserId = localStorage.getItem('currentUserId') || null;
    let currentSpotId = null;

    // DOM 요소
    const title         = document.querySelector('.gmaps-title');
    const loginBtn      = document.getElementById('loginBtn');
    const menuBtn       = document.querySelector('.gmaps-menu');
    const menuPanel     = document.getElementById('menuPanel');
    const menuClose     = document.getElementById('menuClose');
    const modalOverlay  = document.getElementById('modalOverlay');
    const cancelBtn     = document.getElementById('cancelBtn');
    const confirmBtn    = document.getElementById('confirmBtn');
    // 로그인/회원가입 모달 탭
    const showLogin     = document.getElementById('showLogin');
    const showSignup    = document.getElementById('showSignup');
    const loginForm     = document.getElementById('loginForm');
    const signupFormModal = document.getElementById('signupFormModal');
    const searchInput   = document.getElementById('mapSearch');
    const searchBtn     = document.querySelector('.gmaps-search button');
    const modeBtns      = document.querySelectorAll('.mode-btn');
    const openFreeBoard = document.getElementById('openFreeBoard');
    const boardModal    = document.getElementById('boardModal');
    const cancelBoardBtn= document.getElementById('cancelBoardBtn');
    const registerBoardBtn = document.getElementById('registerBoardBtn');
    const openFavorites = document.getElementById('openFavorites');
    const favModal      = document.getElementById('favModal');
    const cancelFavBtn  = document.getElementById('cancelFavBtn');
    const favList       = document.getElementById('favList');
    const sidePanel     = document.getElementById('sidePanel');
    const sideClose     = document.getElementById('sideClose');
    const sideContent   = document.getElementById('sideContent');
    const boardListModal = document.getElementById('boardListModal');
    const closeBoardList = document.getElementById('closeBoardList');
    const boardList = document.getElementById('boardList');

    // 로그인 버튼 텍스트 업데이트
    function updateLoginBtn() {
      loginBtn.textContent = currentUserId ? '로그아웃' : '로그인';
    }

    // 타이틀 클릭 시 새로고침 (로그인 유지)
    title.addEventListener('click', () => window.location.reload());

    // 로그인/로그아웃 핸들러
    loginBtn.addEventListener('click', () => {
      if (currentUserId) {
        fetch('/api/logout', { method: 'POST', credentials: 'include' })
          .then(() => {
            alert('로그아웃 되었습니다.');
            currentUserId = null;
            localStorage.removeItem('currentUserId');
            location.reload();  // ✅ 새로고침으로 반영
          });
      } else {
        modalOverlay.classList.remove('hidden');
        // 기본 탭은 로그인
        showLogin.click();
      }
    });

    // 모달 내 탭 전환
    showLogin.addEventListener('click', () => {
      signupFormModal.classList.add('hidden');
      loginForm.classList.remove('hidden');
    });
    showSignup.addEventListener('click', () => {
      loginForm.classList.add('hidden');
      signupFormModal.classList.remove('hidden');
    });

    // 모달 취소
    cancelBtn.addEventListener('click', () => modalOverlay.classList.add('hidden'));

    // 로그인 확인
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault(); // 기본 제출 방지

      const userId = document.getElementById('userId').value.trim();
      const userPw = document.getElementById('userPw').value;

      try {
        const res = await fetch('/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ user_id: userId, user_pw: userPw })
        });

        const data = await res.json().catch(() => null);

        if (res.ok && data?.result === '성공') {
          localStorage.setItem('currentUserId', data.user_id);

          // 세션 확인 후 로그인 버튼 업데이트
          const checkRes = await fetch('/api/check-login', { credentials: 'include' });
          const checkData = await checkRes.json();

          if (checkData.logged_in) {
            alert('로그인 성공!');
            await checkSessionAndUpdate();
            location.reload();  // ✅ 새로고침으로 로그인 UI 반영
          } else {
            alert('세션 확인 실패, 다시 시도해주세요.');
          }
        } else {
          alert(`로그인 실패: ${data?.error || '서버 오류'}`);
        }

      } catch (err) {
        alert('서버 오류 발생');
      }
    });

    // 회원가입 처리
    signupFormModal.addEventListener('submit', async e => {
      e.preventDefault();
      const form = e.currentTarget;
      const data = {
        user_id: form.user_id.value.trim(),
        user_pw: form.user_pw.value,
        name:    form.name.value.trim(),
        email:   form.email.value.trim(),
        address: form.address.value.trim(),
        phone:   form.phone.value.trim()
      };
      try {
        const res = await fetch('/api/create/users', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        const json = await res.json();
        if (res.ok) {
          alert('회원가입이 완료되었습니다. 로그인해주세요.');
          showLogin.click();
        } else {
          alert(`회원가입 실패: ${json.error}`);
        }
      } catch {
        alert('서버 통신 오류, 다시 시도해주세요.');
      }
    });

    // Kakao Map 초기화
    if (!window.kakao || !kakao.maps) return console.error('Kakao Maps SDK 실패');
    const map = new kakao.maps.Map(document.getElementById('map'), {
      center: new kakao.maps.LatLng(36.5, 127.8),
      level: 13,
      draggable: true,
      scrollWheel: false
    });
    window.addEventListener('resize', () => {
      const center = map.getCenter(); map.relayout(); map.setCenter(center);
    });
    const clusterer = new kakao.maps.MarkerClusterer({ map, averageCenter: true, minLevel: 5 });
    const redIcon = new kakao.maps.MarkerImage(
      'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/marker_red.png',
      new kakao.maps.Size(27, 40)
    );
    let allMarkers = [];

    // 스팟 로드 및 마커 생성
    let spotsLoaded = false;

    fetch('/api/spots')
      .then(res => res.json())
      .then(spots => {
        allMarkers = spots.map(spot => {
          const pos = new kakao.maps.LatLng(spot.coords[1], spot.coords[0]);
          const marker = new kakao.maps.Marker({ position: pos, image: spot.type === '실내' ? redIcon : undefined });
          kakao.maps.event.addListener(marker, 'click', () => showSpot(spot, pos));
          return { spot, marker };
        });
        updateMarkers();
        spotsLoaded = true; // ✅ 여기가 중요!
      })
      .catch(err => console.error('스팟 로드 오류', err));

    // 스팟 정보 표시
    function showSpot(spot, pos) {
      currentSpotId = spot.spot_id;
      map.setCenter(pos); map.setLevel(6);
      sideContent.innerHTML = renderSpotHTML(spot);
      attachSaveHandler();
      const [lng, lat] = spot.coords;
      fillWeather('weather1', `/api/weather?lat=${lat}&lng=${lng}`);
      fillShortTermWeather('weather2', `/api/weather?lat=${lat}&lng=${lng}`);
      fillMidWeather('weather3', `/api/weather?lat=${lat}&lng=${lng}`);
      renderHourlyForecast('hourlyWeather', lat, lng);
      loadFishInfo(lat, lng);
      sidePanel.classList.add('open');
    }

    // 스팟 HTML
    function renderSpotHTML(s) {
      return `
        <div class="info-card">
          <img src="${s.thumbnail}" class="info-img" alt="${s.name}" onerror="this.onerror=null;this.src='/static/images/default.png';" />
          <div class="info-title">${s.name}</div>
          <div class="info-rating">
            <span class="rating-value">${s.rating ?? '4.2'}</span>
            <span class="stars">${'★'.repeat(Math.round(s.rating ?? 4)) + '☆'.repeat(5 - Math.round(s.rating ?? 4))}</span>
            <span class="reviews">(${s.reviews ?? 13})</span>
          </div>
          <div class="info-type-phone">
            <span>${s.type}</span>
            <span style="margin-left:auto;">${s.tel || '정보없음'}</span>
          </div>
          <div class="info-address"><i class="fas fa-map-marker-alt"></i>${s.address}</div>
          <button class="save-btn px-4 py-2 bg-blue-600 text-white rounded">저장</button>
        </div>
        <div class="flex gap-4 mt-4">
          <div id="weather1" class="info-box"></div>
          <div id="weather2" class="info-box"></div>
          <div id="weather3" class="info-box"></div>
        </div>
        <div id="hourlyWeather" class="hourly-weather mt-4"></div>
        <div id="fishInfo" class="info-box mt-4">
          <h2 class="text-xl mb-2">물고기 정보</h2>
          <div class="fish-list flex-col gap-3"></div>
        </div>
      `;
    }

    // 마커 업데이트
    function updateMarkers() {
      clusterer.clear();
      const mode = document.querySelector('.mode-btn.active').dataset.mode;
      clusterer.addMarkers(allMarkers.filter(m => m.spot.type === mode).map(m => m.marker));
    }
    modeBtns.forEach(btn => btn.addEventListener('click', () => {
      modeBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active'); sidePanel.classList.remove('open'); updateMarkers();
    }));

    // 검색
    function handleSearch() {
      const term = searchInput.value.trim().toLowerCase(); if (!term) return;
      const found = allMarkers.find(m => m.spot.name.toLowerCase().includes(term));
      found ? kakao.maps.event.trigger(found.marker, 'click') : alert('검색 결과가 없습니다.');
    }
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', e => { if (e.key === 'Enter') handleSearch(); });

    // 사이드패널 닫기
    sideClose.addEventListener('click', () => sidePanel.classList.remove('open'));

    // 햄버거 메뉴 토글
    menuBtn.addEventListener('click', () => menuPanel.classList.toggle('open'));
    menuClose.addEventListener('click', () => menuPanel.classList.remove('open'));

    // 자유게시판
    openFreeBoard.addEventListener('click', () => {
      if (!spotsLoaded) {
        alert('낚시터 정보를 아직 불러오는 중입니다. 잠시 후 다시 시도해주세요.');
        return;
      }

      boardListModal.classList.remove('hidden');
      menuPanel.classList.remove('open');
      loadBoardList();
    });

    cancelBoardBtn.addEventListener('click', () => boardModal.classList.add('hidden'));
    registerBoardBtn.addEventListener('click', () => {
      if (!currentUserId) return alert('로그인 후 이용해주세요');
      
      const spotId = document.getElementById('boardSpotSelect').value || null;

      fetch('/api/boards', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: currentUserId,
          title: document.getElementById('boardTitle').value,
          content: document.getElementById('boardContent').value,
          spot_id: spotId
        })
      })
      .then(res => res.json())
      .then(d => alert(d.result === '성공' ? '게시글 등록 완료' : d.error))
      .finally(() => boardModal.classList.add('hidden'));
    });

    // 즐겨찾기 목록 & 이동
    openFavorites.addEventListener('click', () => {
      if (!currentUserId) return alert('로그인 후 이용해주세요');
      favModal.classList.remove('hidden'); loadFavorites();
    });
    cancelFavBtn.addEventListener('click', () => favModal.classList.add('hidden'));

    function loadFavorites() {
      favList.innerHTML = '<p>로딩 중...</p>';
      fetch(`/api/favorites?user_id=${currentUserId}`)
        .then(res => res.json())
        .then(data => {
          favList.innerHTML = '';
          if (!data.data || data.data.length === 0) {
            favList.innerHTML = '<p>즐겨찾기가 없습니다.</p>';
            return;
          }

          data.data.forEach(item => {
            const div = document.createElement('div');
            div.className = 'flex justify-between items-center py-2 px-2 hover:bg-gray-100 rounded';

            const spotText = document.createElement('span');
            spotText.className = 'cursor-pointer text-blue-700 hover:underline';
            spotText.textContent = `${item.name} (${item.address})`;
            spotText.addEventListener('click', () => {
              favModal.classList.add('hidden');
              menuPanel.classList.remove('open');

              if (!allMarkers.length) {
                alert('지도가 아직 로딩되지 않았습니다. 잠시 후 다시 시도해주세요.');
                return;
              }

              const match = allMarkers.find(m => Number(m.spot.spot_id) === Number(item.spot_id));
              if (match) {
                kakao.maps.event.trigger(match.marker, 'click');
              } else {
                alert(`해당 낚시터(spot_id: ${item.spot_id})를 찾을 수 없습니다.`);
              }
            });

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'text-red-500 hover:text-red-700 ml-4 text-sm';
            deleteBtn.textContent = '✕';
            deleteBtn.addEventListener('click', () => {
              if (!confirm(`'${item.name}'을(를) 즐겨찾기에서 삭제하시겠습니까?`)) return;

              fetch('/api/favorites', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: currentUserId, spot_id: item.spot_id })
              })
              .then(res => res.json())
              .then(result => {
                if (result.result === '삭제 완료') {
                  alert('즐겨찾기에서 삭제되었습니다.');
                  loadFavorites(); // 목록 갱신
                } else {
                  alert(result.error || '삭제 실패');
                }
              })
              .catch(() => alert('서버 오류로 삭제에 실패했습니다.'));
            });

            div.appendChild(spotText);
            div.appendChild(deleteBtn);
            favList.appendChild(div);
          });
        })
        .catch(() => {
          favList.innerHTML = '<p class="text-red-500">불러오는 중 오류 발생</p>';
        });
    }

    function loadBoardList() {
      boardList.innerHTML = '<p class="text-gray-400">로딩 중...</p>';

      fetch('/api/boards')
        .then(res => res.json())
        .then(data => {
          if (!data.boards || data.boards.length === 0) {
            boardList.innerHTML = '<p class="text-gray-500">게시글이 없습니다.</p>';
            return;
          }
          boardList.innerHTML = '';
          data.boards.forEach(board => {
            const div = document.createElement('div');
            div.className = 'p-4 bg-gray-100 rounded-lg shadow hover:bg-blue-100 cursor-pointer';
            div.innerHTML = `
              <div class="font-bold">${board.title}</div>
              <div class="text-sm text-gray-600">${board.user_id} | ${new Date(board.reg_date).toLocaleString()}</div>
              <div class="mt-1 text-gray-700 text-sm truncate">${board.content}</div>
            `;
            div.addEventListener('click', () => {
              document.getElementById('boardDetailModal').dataset.boardId = board.board_id;

              document.getElementById('detailTitle').textContent = board.title;
              document.getElementById('detailMeta').textContent = `${board.user_id} | ${new Date(board.reg_date).toLocaleString()}`;
              document.getElementById('detailContent').textContent = board.content;
              document.getElementById('boardDetailModal').classList.remove('hidden');

              // ✅ 로딩 표시 추가
              document.getElementById('detailSpot').innerHTML = '<p class="text-gray-400">낚시터 정보를 불러오는 중...</p>';
              document.getElementById('commentList').innerHTML = '<p class="text-gray-400">댓글을 불러오는 중...</p>';

              setTimeout(() => {
                const spotLink = document.getElementById('goToSpot');
                if (spotLink) {
                  spotLink.addEventListener('click', () => {
                    const spotId = Number(spotLink.dataset.spotId);
                    const target = allMarkers.find(({ spot }) => Number(spot.spot_id) === spotId);
                    if (target) {
                      const pos = target.marker.getPosition();
                      showSpot(target.spot, pos);
                      document.getElementById('boardDetailModal').classList.add('hidden');
                    } else {
                      alert('해당 낚시터를 지도에서 찾을 수 없습니다.');
                    }
                  });
                }
              }, 0);

              // 댓글 로딩
              loadComments(board.board_id);

              // 낚시터 정보 로딩
              fetch(`/api/boards/${board.board_id}`)
                .then(res => res.json())
                .then(data => {
                  if (data.spot) {
                    const spot = data.spot;
                    const spotHtml = `
                      <div class="font-semibold text-base mb-1">관련 낚시터</div>
                      <div class="cursor-pointer text-blue-700 hover:underline" id="goToSpot" data-spot-id="${spot.spot_id}">
                        ${spot.name}
                      </div>
                      <div class="text-gray-500">${spot.address}</div>
                      <div class="text-gray-500">${spot.tel || '연락처 없음'}</div>
                    `;
                    document.getElementById('detailSpot').innerHTML = spotHtml;

                    const spotLink = document.getElementById('goToSpot');
                    if (spotLink) {
                      spotLink.addEventListener('click', () => {
                        const spotId = Number(spotLink.dataset.spotId);
                        const target = allMarkers.find(({ spot }) => Number(spot.spot_id) === spotId);
                        if (target) {
                          const pos = target.marker.getPosition();
                          showSpot(target.spot, pos);
                          document.getElementById('boardDetailModal').classList.add('hidden');
                        } else {
                          alert('해당 낚시터를 지도에서 찾을 수 없습니다.');
                        }
                      });
                    }
                  } else {
                    document.getElementById('detailSpot').innerHTML = '<p class="text-gray-500">관련 낚시터 없음</p>';
                  }
                });

              // 수정/삭제 버튼 표시 조건
              const actions = document.getElementById('detailActions');
              if (board.user_id === currentUserId) {
                actions.classList.remove('hidden');

                document.getElementById('editBoardBtn').onclick = () => {
                  const newTitle = prompt('새 제목을 입력하세요', board.title);
                  const newContent = prompt('새 내용을 입력하세요', board.content);
                  if (!newTitle || !newContent) return;

                  fetch(`/api/boards/${board.board_id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title: newTitle, content: newContent })
                  })
                  .then(res => res.json())
                  .then(result => {
                    if (result.result === '수정 완료') {
                      alert('게시글이 수정되었습니다.');
                      document.getElementById('boardDetailModal').classList.add('hidden');
                      loadBoardList();
                    } else {
                      alert(result.error || '수정 실패');
                    }
                  });
                };

                document.getElementById('deleteBoardBtn').onclick = () => {
                  if (!confirm('정말 삭제하시겠습니까?')) return;

                  fetch(`/api/boards/${board.board_id}`, { method: 'DELETE' })
                    .then(res => res.json())
                    .then(result => {
                      if (result.result === '삭제 완료') {
                        alert('게시글이 삭제되었습니다.');
                        document.getElementById('boardDetailModal').classList.add('hidden');
                        loadBoardList();
                      } else {
                        alert(result.error || '삭제 실패');
                      }
                    });
                };

              } else {
                actions.classList.add('hidden');
              }
            });

            boardList.appendChild(div);
          });
        })
        .catch(() => {
          boardList.innerHTML = '<p class="text-red-500">목록 불러오기 실패</p>';
        });
    }


    closeBoardList.addEventListener('click', () => {
      boardListModal.classList.add('hidden');
    });

    // ✅ 상세보기 닫기 버튼 이벤트
    document.getElementById('closeBoardDetail').addEventListener('click', () => {
      const modal = document.getElementById('boardDetailModal');
      modal.classList.add('hidden');
      modal.dataset.boardId = '';
      document.getElementById('detailTitle').textContent = '';
      document.getElementById('detailMeta').textContent = '';
      document.getElementById('detailContent').textContent = '';
      document.getElementById('detailSpot').innerHTML = '';
      document.getElementById('commentList').innerHTML = '';
      document.getElementById('detailActions').classList.add('hidden');
    });

    function attachSaveHandler() {
      const btn = sideContent.querySelector('.save-btn');
      if (!btn || !currentUserId || !currentSpotId) return;

      const updateButtonState = () => {
        fetch(`/api/favorites?user_id=${currentUserId}`)
          .then(res => res.json())
          .then(data => {
            const isSaved = data.data?.some(fav => Number(fav.spot_id) === Number(currentSpotId));
            btn.textContent = isSaved ? '즐겨찾기 취소' : '저장';
            btn.classList.toggle('bg-red-600', isSaved);
            btn.classList.toggle('bg-blue-600', !isSaved);
          });
      };

      updateButtonState(); // 초기 상태 설정

      btn.onclick = () => {
        fetch(`/api/favorites?user_id=${currentUserId}`)
          .then(res => res.json())
          .then(data => {
            const isSaved = data.data?.some(fav => Number(fav.spot_id) === Number(currentSpotId));

            if (isSaved) {
              // 삭제
              fetch('/api/favorites', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: currentUserId, spot_id: currentSpotId })
              })
              .then(res => res.json())
              .then(result => {
                if (result.result === '삭제 완료') {
                  alert('즐겨찾기에서 제거되었습니다.');
                  updateButtonState(); // 다시 상태 갱신
                } else {
                  alert(result.error || '삭제 실패');
                }
              });
            } else {
              // 저장
              fetch('/api/favorites', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: currentUserId, spot_id: currentSpotId, memo: '' })
              })
              .then(res => res.json())
              .then(result => {
                if (result.result === '성공') {
                  alert('즐겨찾기에 추가되었습니다.');
                  updateButtonState(); // 다시 상태 갱신
                } else {
                  alert(result.error || '저장 실패');
                }
              });
            }
          });
      };
    }


    function focusSpot(spotId) {
      favModal.classList.add('hidden');
      const target = allMarkers.find(({ spot }) => spot.spot_id === spotId);
      if (target) {
        const pos = target.marker.getPosition();
        showSpot(target.spot, pos);  // ✅ 마커 클릭 없이 직접 처리
      } else {
        alert('해당 스팟을 찾을 수 없습니다.');
      }
    }

    // 날씨 렌더링 함수들
    function fillWeather(id, url) {
      fetch(url).then(r=>r.json()).then(data=>{
        const c=document.getElementById(id);
        if (data.ultra) {
          const t = Object.keys(data.ultra).sort()[0], info = data.ultra[t];
          c.innerHTML = `<h2 class="font-bold mb-1">${t.slice(0,4)}-${t.slice(4,6)}-${t.slice(6,8)} ${t.slice(8,10)}:${t.slice(10,12)}</h2>` +
                        `<p class="text-sm">온도: ${info.temperature ?? '-'}°C</p>` +
                        `<p class="text-sm">풍속: ${info.wind_speed ?? '-'} m/s</p>` +
                        `<p class="text-sm">강수확률: ${info.precipitation_probability ?? '-'}%</p>` +
                        `<p class="text-sm">파고: ${info.wave_height ?? '-'} m</p>`;
        } else c.innerHTML = '<p class="text-red-500 text-sm">초단기 데이터 없음</p>';
      }).catch(_=>document.getElementById(id).innerHTML='<p class="text-red-500 text-sm">초단기 로드 실패</p>');
    }
    function fillShortTermWeather(id, url) {
      fetch(url).then(r=>r.json()).then(data=>{
        const c=document.getElementById(id);
        if (data.short) {
          const tomorrow = new Date(); tomorrow.setDate(tomorrow.getDate()+1);
          const d = tomorrow.toISOString().slice(0,10).replace(/-/g,''), entry = Object.entries(data.short).find(([dt])=>dt.startsWith(d));
          if (entry) {
            const [dt, info] = entry;
            c.innerHTML = `<h2 class="font-bold mb-1">${dt.slice(0,4)}-${dt.slice(4,6)}-${dt.slice(6,8)} ${dt.slice(8,10)}:${dt.slice(10,12)}</h2>` +
                          `<p class="text-sm">온도: ${info.temperature ?? '-'}°C</p>` +
                          `<p class="text-sm">강수확률: ${info.precipitation_probability ?? '-'}%</p>` +
                          `<p class="text-sm">풍속: ${info.wind_speed ?? '-'} m/s</p>` +
                          `<p class="text-sm">파고: ${info.wave_height ?? '-'} m</p>`;
            return;
          }
        }
        c.innerHTML = '<p class="text-red-500 text-sm">단기 데이터 없음</p>';
      }).catch(_=>document.getElementById(id).innerHTML='<p class="text-red-500 text-sm">단기 로드 실패</p>');
    }
    function fillMidWeather(id, url) {
        fetch(url).then(res => res.json()).then(data => {
          const container = document.getElementById(id);
          container.innerHTML = '';
          if (data.mid?.land) {
            Object.entries(data.mid.land).slice(0, 5).forEach(([dt, info]) => {
              const dateStr = `${dt.slice(0,4)}-${dt.slice(4,6)}-${dt.slice(6,8)}`;
              container.innerHTML += `
                <div class="mb-3">
                  <div class="font-semibold">${dateStr}</div>
                  <p>최저 ${info.temperature_min_4 ?? '-'}°C / 최고 ${info.temperature_max_4 ?? '-'}°C</p>
                  <p>강수확률 ${info.precipitation_probability ?? '-'}%</p>
                  <p>풍속 ${info.wind_speed ?? '-'} m/s</p>
                </div>`;
            });
          } else {
            container.innerHTML = '<p class="text-red-500">중기 데이터 없음</p>';
          }
        }).catch(() => {
          document.getElementById(id).innerHTML = '<p class="text-red-500">중기 로드 실패</p>';
        });
      }

    function renderHourlyForecast(containerId, lat, lng) {
      const container = document.getElementById(containerId);
      container.innerHTML = '';
      fetch(`/api/weather?lat=${lat}&lng=${lng}`).then(r=>r.json()).then(data=>{
        const list = { ...(data.ultra || {}), ...(data.short || {}) };
        Object.entries(list).sort(([a],[b])=>a.localeCompare(b)).slice(0,6).forEach(([dt,info])=>{
          const hour = dt.slice(8,10), temp = info.temperature ?? '-', pop = info.precipitation_probability ?? info.precipitation ?? 0;
          let icon = 'fas fa-sun';
          if (info.precipitation_type > 0) icon = 'fas fa-cloud-showers-heavy';
          else if (info.sky === 3) icon = 'fas fa-cloud';
          else if (info.sky === 1) icon = 'fas fa-cloud-sun';
          const item = document.createElement('div');
          item.className = 'hour-item';
          item.innerHTML = `<div class="hour-label">${hour}:00</div>` +
                            `<i class="${icon} weather-icon"></i>` +
                            `<div class="temp-label">${temp}°</div>` +
                            `<div class="precip-container"><div class="precip-bar" style="height:${Math.round(pop)}%;"></div></div>` +
                            `<div class="precip-label">${pop}%</div>`;
          container.append(item);
        });
      });
    }
    /** 위키피디아 썸네일 */
    function fetchWikipediaThumbnail(species) {
      const url = `https://ko.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(species)}`;
      return fetch(url).then(res => res.ok ? res.json() : Promise.reject()).then(json => json.thumbnail?.source || '/static/images/dolphin.svg').catch(() => '/static/images/dolphin.svg');
    }
    /** 물고기 정보 */
    function loadFishInfo(lat, lng) {
      const container = sideContent.querySelector('#fishInfo .fish-list');
      container.innerHTML = '';
      fetch(`/api/fish/by-coords?lat=${lat}&lng=${lng}`)
        .then(res => res.json())
        .then(list => Promise.all(list.map(f => fetchWikipediaThumbnail(f.species).then(img => ({ ...f, img }))))
        .then(items => {
          items.forEach(({species,percent,img}) => {
            const wrap = document.createElement('div'); wrap.className = 'flex items-center gap-3';
            wrap.innerHTML = `<a href="https://ko.wikipedia.org/wiki/${encodeURIComponent(species)}" target="_blank" rel="noopener"><img src="${img}" alt="${species}" class="rounded-md w-16 h-16 object-cover cursor-pointer"/></a>` +
                              `<div><div class="font-semibold">${species}</div><div class="text-sm text-gray-500">${percent}%</div></div>`;
            container.append(wrap);
          });
        }))
        .catch(err => console.error('물고기 정보 로드 오류', err));
    }

    async function checkSessionAndUpdate() {
    try {
      const res = await fetch('/api/check-login', { credentials: 'include' });
      const data = await res.json();

      if (data.logged_in) {
        currentUserId = data.user_id;
        localStorage.setItem('currentUserId', currentUserId);
      } else {
        currentUserId = null;
        localStorage.removeItem('currentUserId');
      }

      updateLoginBtn();
    } catch (err) {
      console.error('세션 확인 실패:', err);
    }
  }

    menuBtn.addEventListener('click', () => {
      menuPanel.classList.add('open');
    });
    menuClose.addEventListener('click', () => {
      menuPanel.classList.remove('open');
    });
    document.getElementById('menuOverlay').addEventListener('click', () => {
      menuPanel.classList.remove('open');
    });

    document.getElementById('newBoardBtn').addEventListener('click', () => {
      boardListModal.classList.add('hidden');     // 목록 모달 닫기
      boardModal.classList.remove('hidden');      // 글쓰기 모달 열기
    });

    document.getElementById('commentSubmit').addEventListener('click', () => {
      const input = document.getElementById('commentInput');
      const content = input.value.trim();
      const boardId = Number(document.getElementById('boardDetailModal').dataset.boardId);

      if (!currentUserId) return alert('로그인 후 이용해주세요');
      if (!content) return alert('내용을 입력해주세요');

      fetch('/api/comments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ board_id: boardId, user_id: currentUserId, comment_content: content })
      })
      .then(res => res.json())
      .then(data => {
        if (data.result === '성공') {
          input.value = '';
          loadComments(boardId);  // 목록 새로고침
        } else {
          alert(data.error || '작성 실패');
        }
      });
    });


    function loadComments(boardId) {
      const list = document.getElementById('commentList');
      list.innerHTML = '<p class="text-gray-400">불러오는 중...</p>';

      fetch(`/api/comments?board_id=${boardId}`)
        .then(res => res.json())
        .then(data => {
          list.innerHTML = '';
          if (!data.comments || data.comments.length === 0) {
            list.innerHTML = '<p class="text-gray-400">댓글이 없습니다.</p>';
            return;
          }

          data.comments.forEach(comment => {
            const div = document.createElement('div');
            div.className = 'p-2 bg-gray-100 rounded';

            const header = document.createElement('div');
            header.className = 'text-sm text-gray-600 flex justify-between';
            header.innerHTML = `<span>${comment.user_id} | ${new Date(comment.comment_date).toLocaleString()}</span>`;

            // 삭제 버튼: 본인일 때만
            if (comment.user_id === currentUserId) {
              const delBtn = document.createElement('button');
              delBtn.textContent = '삭제';
              delBtn.className = 'text-red-500 text-sm hover:underline ml-2';
              delBtn.addEventListener('click', () => {
                if (!confirm('댓글을 삭제하시겠습니까?')) return;
                fetch(`/api/comments/${comment.comment_id}`, {
                  method: 'DELETE',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ user_id: currentUserId })
                })
                .then(res => res.json())
                .then(d => {
                  if (d.result === '성공') {
                    alert('삭제되었습니다.');
                    loadComments(boardId);
                  } else {
                    alert(d.error || '삭제 실패');
                  }
                });
              });
              header.appendChild(delBtn);
            }

            const content = document.createElement('div');
            content.className = 'mt-1';
            content.textContent = comment.comment_content;

            div.appendChild(header);
            div.appendChild(content);
            list.appendChild(div);
          });
        });
    }

function loadSpotOptions() {
  const select = document.getElementById('boardSpotSelect');
  if (!select || !currentUserId) return;

  // 초기 옵션 비우고 기본 안내 추가
  select.innerHTML = '<option value="">낚시터를 선택하세요 (선택사항)</option>';

  fetch(`/api/favorites?user_id=${currentUserId}`)
    .then(res => res.json())
    .then(data => {
      if (!data.data || data.data.length === 0) {
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = '즐겨찾기한 낚시터가 없습니다.';
        select.appendChild(opt);
        return;
      }

      data.data.forEach(item => {
        const opt = document.createElement('option');
        opt.value = item.spot_id;
        opt.textContent = `${item.name} (${item.address})`;
        select.appendChild(opt);
      });
    })
    .catch(() => {
      const opt = document.createElement('option');
      opt.value = '';
      opt.textContent = '즐겨찾기 로드 실패';
      select.appendChild(opt);
    });
}
    loadSpotOptions(); // 페이지 로드 시 실행


    checkSessionAndUpdate(); 
  });
