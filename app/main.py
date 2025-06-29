from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from app.routes.companies import router as company_router
from app.routes.stocks import router as stock_router

app = FastAPI(title="Stock Assistance")

app.include_router(company_router)
app.include_router(stock_router)