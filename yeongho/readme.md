### README.md (markdown snippet)

# 📰 뉴스 키워드/세터 배열 분석 대시보드 (FastAPI 기반)

구구 뉴스로부터 키워드와 세터 기준으로 기사를 수집하고, 집계 및 시각화를 통해 대시보드 형태로 보여주는 프로젝트입니다.

---

## ✅ 주요 기능

- 📱 **뉴스 수집**: 구구 뉴스 RSS 기반 자동 수집
- 📊 **뉴스 집계**: 세터 및 키워드 기준 기사 수 집계
- 📈 **차트 시각화**: Matplotlib로 이미지 차트 생성
- 🖼️ **웹 대시보드**: FastAPI + Jinja2로 차트 HTML 렌더링

---

## ⚙️ 설치 방법

```bash
# 1. 가상 환경 설정
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. 필수 라이브러리 설치
pip install -r requirements.txt
```

📦 requirements.txt 예시:

```
fastapi
uvicorn
pandas
matplotlib
feedparser
beautifulsoup4
scikit-learn
apscheduler
jinja2
```

---

## 🚀 실행 방법

```bash
uvicorn yeongho.main:app --reload
```

FastAPI 서버가 실행되면 다음 같은 경로로 접속할 수 있습니다:

- [http://localhost:8000](http://localhost:8000) : 대시보드 메인 화면
- [http://localhost:8000/collect-news](http://localhost:8000/collect-news) : 뉴스 수집 실행
- [http://localhost:8000/aggregate-news](http://localhost:8000/aggregate-news) : 기사 수 집계 실행
- [http://localhost:8000/generate-charts](http://localhost:8000/generate-charts) : 차트 이미지 생성
- [http://localhost:8000/view/keyword/인공지능](http://localhost:8000/view/keyword/인공지능) : 키워드별 차트 확인
- [http://localhost:8000/view/sector/AI](http://localhost:8000/view/sector/AI) : 세터별 차트 확인
- [http://localhost:8000/view/sector](http://localhost:8000/view/sector) : 전체 세터 차트 확인

---

## ⏱️ 자동 뉴스 수집 스컴지어

프로젝트는 자동으로 뉴스 수집을 주기적으로 수행합니다. 이는 `yeongho/core/scheduler.py`에 정의된 시간표에 따라 실행됩니다.

기본 수집 시간:

- ⏰ 06:30
- ⏰ 10:00
- ⏰ 12:00
- ⏰ 15:00
- ⏰ 18:00
- ⏰ 21:00

해당 시간만법 `collect-news` 역할이 복잡되어 자동 수집이 진행됩니다.

수동 실행을 원하면 아래 명령을 사용하세요:

```bash
curl http://localhost:8000/collect-news
```
