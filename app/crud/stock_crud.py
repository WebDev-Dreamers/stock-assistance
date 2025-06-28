import pandas as pd
from app.models.models import Stock, Company
from sqlalchemy.orm import Session
from app.database import SessionLocal


def save_stock_records(db: Session, company: Company, df: pd.DataFrame):
    for _, row in df.iterrows():
        stock = Stock(
            stock_name=company.company_name,
            stock_code=company.company_code,
            sector_id=company.sector_id,
            trade_date=pd.to_datetime(row["일자"]),
            opening_price=float(str(row["시가"]).replace(",", "") or 0),
            highest_price=float(str(row["고가"]).replace(",", "") or 0),
            lowest_price=float(str(row["저가"]).replace(",", "") or 0),
            closing_price=float(str(row["종가"]).replace(",", "") or 0),
            trading_volume=int(str(row["거래량"]).replace(",", "") or 0),
            trade_value=int(str(row["거래대금"]).replace(",", "") or 0),
            market_cap=int(str(row["시가총액"]).replace(",", "") or 0),
        )
        db.add(stock)
    db.commit()