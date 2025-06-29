from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import os
import json
import pandas as pd

# --- 내부 모듈 임포트 ---
from yeongho.crawler import load_keywords, collect_google_news_by_keywords
from yeongho.aggregate_news import aggregate_news_counts
from yeongho.plot_chart import generate_sector_charts, generate_keyword_charts, generate_issue_charts

# --- FastAPI 앱 초기화 ---
app = FastAPI()

# --- CORS 설정 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 정적 파일 및 템플릿 설정 ---
app.mount("/static", StaticFiles(directory="yeongho/IMG"), name="static")
templates = Jinja2Templates(directory="yeongho/templates")


# --- 스케줄러 설정 ---
scheduler = BackgroundScheduler()

def schedule_collect_news():
    try:
        res = requests.get("http://localhost:8000/collect-news")
        print(f"📡 자동 뉴스 수집 호출 완료 - {res.status_code}")
    except Exception as e:
        print(f"❌ 자동 호출 실패: {e}")

for t in ["06:30", "10:00", "12:00", "15:00", "18:00", "21:00"]:
    hour, minute = map(int, t.split(":"))
    scheduler.add_job(schedule_collect_news, 'cron', hour=hour, minute=minute)

scheduler.start()

# --------------------------------------------------
# 📰 뉴스 수집 API
# --------------------------------------------------
@app.get("/collect-news")
async def collect_news():
    try:
        keywords = load_keywords()
        print(f"🔑 수집 대상 키워드 목록: {list(keywords.keys())}")
        collect_google_news_by_keywords(keywords)
        return JSONResponse(content={"status": "S", "message": "✅ 뉴스 수집 완료"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "E", "error": f"뉴스 수집 실패: {str(e)}"})

# --------------------------------------------------
# 📊 뉴스 집계 API
# --------------------------------------------------
@app.get("/aggregate-news")
async def aggregate_news():
    try:
        aggregate_news_counts()
        return JSONResponse(content={"status": "S", "message": "✅ 뉴스 집계 완료"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "E", "error": f"집계 실패: {str(e)}"})

# --------------------------------------------------
# 📈 차트 생성 API
# --------------------------------------------------
@app.get("/generate-charts")
async def generate_charts():
    try:
        generate_sector_charts()
        generate_keyword_charts()
        generate_issue_charts()
        return JSONResponse(content={"status": "S", "message": "✅ 차트 생성 완료"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "E", "error": f"차트 생성 실패: {str(e)}"})


# --------------------------------------------------
# 🖼️ 대시보드 화면
# --------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def chart_index(request: Request):
    # ✅ 키워드 로드
    with open("yeongho/config/keywords.json", encoding="utf-8") as f:
        keywords_data = json.load(f)
    keyword_list = sorted(keywords_data.keys())

    # ✅ 섹터 로드
    sector_csv = pd.read_csv("yeongho/DATA/sector.csv")
    all_sectors = sector_csv["SECTOR"].dropna().unique()

    # ✅ 일반 섹터 / 이슈 섹터 분리
    sector_list = sorted([s for s in all_sectors if "_이슈" not in s and "_팀" not in s])
    sector_issue_list = sorted([s for s in all_sectors if "_이슈" in s])

    return templates.TemplateResponse("chart_index.html", {
        "request": request,
        "keyword_list": keyword_list,
        "sector_list": sector_list,
        "sector_issue_list": sector_issue_list
    })


@app.get("/view/keyword/{keyword}", response_class=HTMLResponse)
def view_keyword_chart(request: Request, keyword: str):
    suffixes = [("1개월", "daily_1m"), ("3개월", "weekly_3m"), ("1년", "monthly_1y")]
    images = []
    for label, suffix in suffixes:
        filename = f"{keyword}_keyword_{suffix}.png"
        path = f"keyword/{filename}"  # ✅ 디렉토리 경로 추가
        if os.path.exists(os.path.join("yeongho/IMG", path)):
            images.append((label, path))
    return templates.TemplateResponse("chart_detail.html", {
        "request": request,
        "title": keyword,
        "images": images
    })


@app.get("/view/sector/{sector}", response_class=HTMLResponse)
def view_sector_chart(request: Request, sector: str):
    suffixes = [("1개월", "daily_1m"), ("3개월", "weekly_3m"), ("1년", "monthly_1y")]
    images = []

    # ✅ 이슈 섹터는 issue 디렉토리에서 검색
    if "_이슈" in sector:
        folder = "issue"
        title = f"{sector.replace('_이슈', '')} 이슈"
    else:
        folder = "sector"
        title = f"{sector} 섹터"

    for label, suffix in suffixes:
        filename = f"{sector}_{suffix}.png"
        path = f"{folder}/{filename}"
        if os.path.exists(os.path.join("yeongho/IMG", path)):
            images.append((label, path))

    return templates.TemplateResponse("chart_detail.html", {
        "request": request,
        "title": title,
        "images": images
    })


@app.get("/view/sector", response_class=HTMLResponse)
def view_total_sector_chart(request: Request):
    suffixes = [("1개월", "daily_1m"), ("3개월", "weekly_3m"), ("1년", "monthly_1y")]
    images = []
    for label, suffix in suffixes:
        filename = f"sector_{suffix}.png"
        path = f"sector/{filename}"  # ✅ 디렉토리 경로 추가
        if os.path.exists(os.path.join("yeongho/IMG", path)):
            images.append((label, path))
    return templates.TemplateResponse("chart_detail.html", {
        "request": request,
        "title": "전체 섹터",
        "images": images
    })
