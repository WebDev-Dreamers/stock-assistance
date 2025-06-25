from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .database import engine, Base, SessionLocal
from .models import Stock
import datetime

app = FastAPI(title="Stock CRUD API with Frontend")

# DB 초기화
Base.metadata.create_all(bind=engine)

# 템플릿 설정
templates = Jinja2Templates(directory="app/templates")


@app.get("/add", response_class=HTMLResponse)
def add_stock_form(request: Request):
    return templates.TemplateResponse("add_stock.html", {"request": request})

@app.post("/add")
def submit_stock_form(
    request: Request,
    name: str = Form(...),
    code: str = Form(...),
    group: str = Form(...),
    date: str = Form(...),
    open: float = Form(...),
    close: float = Form(...),
    high: float = Form(...),
    low: float = Form(...),
    volume: int = Form(...),
):
    db = SessionLocal()
    stock = Stock(
        name=name, code=code, group=group,
        date=datetime.datetime.strptime(date, "%Y-%m-%d").date(),
        open=open, close=close, high=high, low=low, volume=volume
    )
    db.add(stock)
    db.commit()
    db.close()
    return RedirectResponse(url="/view", status_code=303)

@app.get("/view", response_class=HTMLResponse)
def view_stocks(request: Request):
    db = SessionLocal()
    stocks = db.query(Stock).order_by(Stock.date.desc()).all()
    db.close()
    return templates.TemplateResponse("view_stocks.html", {"request": request, "stocks": stocks})
