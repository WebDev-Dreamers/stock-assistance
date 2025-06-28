from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.services.stock_service import save_init_stock_price

router = APIRouter()


class StockInitRequest(BaseModel):
    stocks: List[str]
    

@router.post("/api/stocks/init-price-data")
def init_price_data(request: StockInitRequest):
    result = save_init_stock_price(request.stocks)
    return result