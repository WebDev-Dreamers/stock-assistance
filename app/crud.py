from sqlalchemy.orm import Session
from . import models, schemas

def create_stock(db: Session, stock: schemas.StockCreate):
    db_stock = models.Stock(**stock.dict())
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock

def get_stock_by_code(db: Session, code: str, limit: int = 100):
    return db.query(models.Stock).filter(models.Stock.code == code).limit(limit).all()

def get_all_stocks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Stock).offset(skip).limit(limit).all()

def delete_stock_by_id(db: Session, stock_id: int):
    stock = db.query(models.Stock).get(stock_id)
    if stock:
        db.delete(stock)
        db.commit()
        return True
    return False
