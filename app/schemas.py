from pydantic import BaseModel
from datetime import date
from typing import Optional

class StockBase(BaseModel):
    date: date
    group: str
    name: str
    code: str
    close: float
    open: float
    high: float
    low: float
    volume: int

class StockCreate(StockBase):
    pass

class StockOut(StockBase):
    id: int

    class Config:
        from_attributes = True
