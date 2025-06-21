// js/board.js
console.log('board.js loaded');

let favorites = [];  // 즐겨찾기 항목 저장 배열

const sectionContent = {
  spots: `
    <h2>즐겨찾기
      <div class="flex mt-2 mb-4">
        <input id="favInput" type="text" placeholder="즐겨찾기 추가…"
               class="flex-1 p-2 rounded-l border-none"/>
        <button id="addFavBtn"
                class="px-4 bg-green-500 text-white rounded-r">
          추가
        </button>
      </div>
    </h2>
    <ul id="favList" class="list-disc pl-5 space-y-2">
      <!-- JS로 동적 생성 -->
    </ul>
  `,
  board: `
    <h2>자유게시판
      <button id="writeBtn" class="px-2 py-1 bg-green-500 text-white rounded float-right">글쓰기</button>
    </h2>
    <div class="search-bar mb-4">
      <input type="text" placeholder="제목 또는 글쓴이 검색…" class="rounded bg-white text-gray-900"/>
    </div>
    <table>
      <thead><tr><th>제목</th><th>글쓴이</th><th>날짜</th></tr></thead>
      <tbody>
        <tr><td><a href="#" class="text-white underline">첫 번째 게시글</a></td><td>관리자</td><td>2025-05-23</td></tr>
        <tr><td><a href="#" class="text-white underline">두 번째 게시글</a></td><td>User01</td><td>2025-05-22</td></tr>
      </tbody>
    </table>
    <div class="pagination">
      <button>&laquo;</button><button class="active">1</button><button>2</button>&hellip;<button>다음</button>
    </div>
  `,
  write: `
    <h2>새 글 작성</h2>
    <form id="postForm" class="space-y-4">
      <div>
        <label>제목</label>
        <input type="text" name="title" class="w-full p-2 rounded border bg-white text-gray-900" required/>
      </div>
      <div>
        <label>내용</label>
        <textarea name="body" rows="6" class="w-full p-2 rounded border bg-white text-gray-900" required></textarea>
      </div>
      <div class="upload-form">
        <label>사진 업로드</label>
        <input type="file" id="postPhoto" accept="image/*"/>
        <img id="postPreview" class="preview" style="display:none;"/>
      </div>
      <div class="flex justify-end space-x-2">
        <button type="button" id="cancelWrite" class="px-4 py-2 bg-gray-400 rounded">취소</button>
        <button type="submit" class="px-4 py-2 bg-indigo-600 text-white rounded">등록</button>
      </div>
    </form>
  `,
  gallery: `
    <h2>사진/동영상 업로드</h2>
    <form id="galleryForm" class="upload-form space-y-4">
      <div>
        <label>이미지 선택</label>
        <input type="file" id="galleryPhoto" accept="image/*" multiple/>
      </div>
      <div id="galleryPreview" class="flex flex-wrap gap-2"></div>
      <button type="submit" class="px-4 py-2 bg-indigo-600 text-white rounded">업로드</button>
    </form>
  `,
  notice: `
    <h2>공지사항</h2>
    <ul class="list-disc pl-5">
      <li>2025-05-20: 정기 점검 안내</li>
      <li>2025-05-15: 신규 기능 출시</li>
    </ul>
  `
};

const contentEl    = document.getElementById('content'),
      sidebarItems = document.querySelectorAll('.sidebar li'),
      homeBtn      = document.getElementById('homeBtn');

// 섹션 전환 함수
function loadSection(key) {
  console.log('loadSection 호출:', key);
  sidebarItems.forEach(li => li.classList.toggle('active', li.dataset.target === key));
  contentEl.innerHTML = sectionContent[key] || '<p>준비 중입니다.</p>';

  if (key === 'spots') {
    // 즐겨찾기 로직
    const input  = document.getElementById('favInput');
    const addBtn = document.getElementById('addFavBtn');
    const listEl = document.getElementById('favList');

    function renderFavs() {
      listEl.innerHTML = '';
      favorites.forEach((item, idx) => {
        const li = document.createElement('li');
        li.className = 'flex justify-between items-center';
        li.innerHTML = `
          <span>${item}</span>
          <button data-idx="${idx}" class="deleteFavBtn px-2 py-0.5 bg-red-500 text-white rounded">
            삭제
          </button>
        `;
        listEl.appendChild(li);
      });
    }

    addBtn.onclick = () => {
      const val = input.value.trim();
      if (!val) return;
      favorites.push(val);
      input.value = '';
      renderFavs();
    };

    listEl.onclick = e => {
      if (!e.target.classList.contains('deleteFavBtn')) return;
      const idx = +e.target.dataset.idx;
      favorites.splice(idx, 1);
      renderFavs();
    };

    renderFavs();
  }

  if (key === 'board') {
    document.getElementById('writeBtn').onclick = () => loadSection('write');
  }
  if (key === 'recommend') {
    document.getElementById('recWriteBtn').onclick = () => loadSection('write');
  }
  if (key === 'write') {
    const photoInput = document.getElementById('postPhoto'),
          preview    = document.getElementById('postPreview');
    photoInput.onchange = () => {
      const file = photoInput.files[0];
      if (!file) return preview.style.display = 'none';
      const reader = new FileReader();
      reader.onload = e => {
        preview.src = e.target.result;
        preview.style.display = 'block';
      };
      reader.readAsDataURL(file);
    };
    document.getElementById('cancelWrite').onclick = () => loadSection('board');
    document.getElementById('postForm').onsubmit = e => {
      e.preventDefault();
      const fd = new FormData(e.target);
      if (photoInput.files[0]) fd.append('photo', photoInput.files[0]);
      fetch('/api/posts', { method:'POST', body:fd })
        .then(r => r.ok ? alert('등록 완료') : alert('등록 실패'));
      loadSection('board');
    };
  }
  if (key === 'gallery') {
    const input            = document.getElementById('galleryPhoto'),
          previewContainer = document.getElementById('galleryPreview');
    input.onchange = () => {
      previewContainer.innerHTML = '';
      Array.from(input.files).forEach(f => {
        const reader = new FileReader();
        reader.onload = e => {
          const img = document.createElement('img');
          img.src       = e.target.result;
          img.className = 'preview rounded';
          previewContainer.appendChild(img);
        };
        reader.readAsDataURL(f);
      });
    };
    document.getElementById('galleryForm').onsubmit = e => {
      e.preventDefault();
      const fd = new FormData();
      Array.from(input.files).forEach(f => fd.append('photos', f));
      fetch('/api/gallery', { method:'POST', body:fd })
        .then(r => r.ok ? alert('업로드 완료') : alert('업로드 실패'));
    };
  }
  if (key === 'spots') initMap();
}

// 사이드바 이벤트
sidebarItems.forEach(li => li.addEventListener('click', () => loadSection(li.dataset.target)));

// 홈 버튼: board.html에서는 기본 이동, 그 외 SPA 모드
if (homeBtn) {
  const isBoardPage = window.location.pathname.endsWith('board.html');
  if (!isBoardPage) {
    homeBtn.addEventListener('click', e => {
      e.preventDefault();
      loadSection('board');
    });
  }
}

// 초기 로드: 자유게시판
loadSection('board');

// 지도 초기화
function initMap() {
  const map = L.map('map').setView([36.5,127.8],7);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution:'© OpenStreetMap contributors'
  }).addTo(map);
}

// ─── 로그인 모달 기능 ────────────────────────────────────────────
document.getElementById('loginBtn').addEventListener('click', () => {
  document.getElementById('modalOverlay').style.display = 'flex';
});
document.getElementById('cancelBtn').addEventListener('click', () => {
  document.getElementById('modalOverlay').style.display = 'none';
});
document.getElementById('confirmBtn').addEventListener('click', () => {
  console.log(`로그인 시도: ID=${document.getElementById('userId').value}`);
  document.getElementById('modalOverlay').style.display = 'none';
});