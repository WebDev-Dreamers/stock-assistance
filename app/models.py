from sqlalchemy import Column, String, Integer, Float, Date
from .database import Base

class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    group = Column(String, index=True)  # 섹터명
    name = Column(String, index=True)   # 종목명
    code = Column(String, index=True)   # 종목코드
    close = Column(Float)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    volume = Column(Integer)
