from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, database

router = APIRouter(prefix="/stocks", tags=["stocks"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.StockOut)
def create_stock(stock: schemas.StockCreate, db: Session = Depends(get_db)):
    return crud.create_stock(db, stock)

@router.get("/", response_model=list[schemas.StockOut])
def read_all_stocks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_all_stocks(db, skip, limit)

@router.get("/{code}", response_model=list[schemas.StockOut])
def read_stock_by_code(code: str, db: Session = Depends(get_db)):
    result = crud.get_stock_by_code(db, code)
    if not result:
        raise HTTPException(status_code=404, detail="Stock not found")
    return result

@router.delete("/{stock_id}")
def delete_stock(stock_id: int, db: Session = Depends(get_db)):
    success = crud.delete_stock_by_id(db, stock_id)
    if not success:
        raise HTTPException(status_code=404, detail="Stock not found")
    return {"deleted": stock_id}
