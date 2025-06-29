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
from yeongho.plot_chart import generate_sector_charts, generate_keyword_charts

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
        return JSONResponse(content={"status": "S", "message": "✅ 차트 생성 완료"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "E", "error": f"차트 생성 실패: {str(e)}"})

# --------------------------------------------------
# 🖼️ 시각화 이미지 렌더링 화면
# --------------------------------------------------
# @app.get("/")
# def show_chart_index(request: Request):
#     sector_dir = "yeongho/IMG"
#     sector_files = os.listdir(sector_dir)

#     # 섹터/키워드 구분 및 고유 이름만 추출
#     names_set = set()
#     for file in sector_files:
#         if file.endswith(".png"):
#             base = file.replace("_daily_1m.png", "").replace("_weekly_3m.png", "").replace("_monthly_1y.png", "")
#             names_set.add(base)

#     sorted_names = sorted(names_set)

#     return templates.TemplateResponse("chart_index.html", {
#         "request": request,
#         "chart_names": sorted_names
#     })


# @app.get("/view/{name}")
# def view_chart_detail(name: str, request: Request):
#     suffixes = ["daily_1m", "weekly_3m", "monthly_1y"]
#     image_paths = [f"{name}_{s}.png" for s in suffixes]

#     return templates.TemplateResponse("chart_detail.html", {
#         "request": request,
#         "name": name,
#         "images": image_paths
#     })

# --------------------------------------------------
# 🖼️ 대시보드 화면
# --------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def chart_index(request: Request):
    with open("yeongho/config/keywords.json", encoding="utf-8") as f:
        keywords_data = json.load(f)
    keyword_list = list(keywords_data.keys())

    sector_csv = pd.read_csv("yeongho/DATA/sector.csv")
    sector_list = sorted(sector_csv["SECTOR"].unique())

    return templates.TemplateResponse("chart_index.html", {
        "request": request,
        "keyword_list": keyword_list,
        "sector_list": sector_list
    })

@app.get("/view/keyword/{keyword}", response_class=HTMLResponse)
def view_keyword_chart(request: Request, keyword: str):
    suffixes = [("1개월", "daily_1m"), ("3개월", "weekly_3m"), ("1년", "monthly_1y")]
    images = []
    for label, suffix in suffixes:
        filename = f"{keyword}_{suffix}.png"
        path = f"{filename}"
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
    for label, suffix in suffixes:
        filename = f"{sector}_{suffix}.png"
        path = f"{filename}"
        if os.path.exists(os.path.join("yeongho/IMG", path)):
            images.append((label, path))
    return templates.TemplateResponse("chart_detail.html", {
        "request": request,
        "title": f"{sector} 섹터",
        "images": images
    })

@app.get("/view/sector", response_class=HTMLResponse)
def view_total_sector_chart(request: Request):
    suffixes = [("1개월", "daily_1m"), ("3개월", "weekly_3m"), ("1년", "monthly_1y")]
    images = []
    for label, suffix in suffixes:
        filename = f"sector_{suffix}.png"
        path = f"{filename}"
        if os.path.exists(os.path.join("yeongho/IMG", path)):
            images.append((label, path))
    return templates.TemplateResponse("chart_detail.html", {
        "request": request,
        "title": "전체 섹터",
        "images": images
    })
