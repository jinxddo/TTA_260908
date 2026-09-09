# 📋 TaskPulse - 스마트 할일관리 웹 애플리케이션 (TTA_260908)

> 파이썬 Flask와 SQLite 기반의 세련된 글래스모피즘(Glassmorphism) UI를 적용한 모던 할일관리(To-Do) 웹 애플리케이션입니다.

---

## ✨ 주요 기능

- **할일 등록 및 관리 (CRUD)**
  - 제목, 상세 메모, 카테고리(업무, 개인, 공부, 기타), 우선순위(높음, 보통, 낮음), 마감일 지정
  - 원클릭 상태 전환(완료/진행 중 토글 및 타임스탬프 자동 기록)
  - 상세 정보 수정 모달 및 안전한 삭제
- **실시간 대시보드 통계**
  - 전체, 진행 중, 완료된 할일 개수 실시간 집계
  - 완료율(%) 프로그레스 바 실시간 시각화
- **실시간 필터링 및 검색**
  - 상태별 탭 필터링 (`전체`, `진행 중`, `완료됨`)
  - 카테고리 및 우선순위 드롭다운 필터
  - 디바운스(Debounce)가 적용된 실시간 키워드 검색
- **사용자 경험 (UX) & 디자인**
  - 최신 글래스모피즘 & 앰비언트 배경 블러 효과
  - 다크 모드 / 라이트 모드 테마 전환 (로컬스토리지 상태 유지)
  - 부드러운 애니메이션 및 작업 알림 토스트(Toast) 피드백
  - 데스크톱 및 모바일 반응형 레이아웃

---

## 🛠️ 기술 스택

- **Backend**: Python 3, Flask 3.1, SQLite3
- **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism Custom Design), JavaScript (ES6+ Fetch API)
- **Testing**: Python `unittest`

---

## 🚀 빠른 시작 가이드 (Getting Started)

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 서버 실행
```bash
python app.py
```

### 3. 브라우저 접속
서버 실행 후 웹 브라우저에서 아래 주소로 접속합니다:
```
http://127.0.0.1:5000
```

---

## 🧪 테스트 실행

```bash
python -m unittest discover -s tests
```
모든 단위 테스트(7건)가 자동으로 수행됩니다.

---

## 📁 프로젝트 구조

```
todo_app/
├── app.py                      # Flask 애플리케이션 및 RESTful API 엔드포인트
├── requirements.txt            # 파이썬 의존성 패키지 목록
├── .gitignore                  # Git 추적 제외 파일 목록
├── README.md                   # 프로젝트 문서
├── templates/
│   └── index.html              # 메인 웹 페이지 마크업
├── static/
│   ├── css/
│   │   └── style.css           # 글래스모피즘 및 테마 스타일시트
│   └── js/
│       └── main.js             # 비동기 CRUD 통신 및 UI 인터랙션 로직
└── tests/
    ├── test_app.py             # 백엔드 API & DB 단위 테스트 (unittest)
    └── verify_live_server.py   # 라이브 서버 HTTP 통합 검증 스크립트
```
