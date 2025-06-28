from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)

    daily_notes = relationship("DailyNote", back_populates="user")


class Sector(Base):
    __tablename__ = "sectors"

    id = Column(Integer, primary_key=True, index=True)
    sector_name = Column(String, unique=True, nullable=False)

    stocks = relationship("Stock", back_populates="sector")
    companies = relationship("Company", back_populates="sector")


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    company_code = Column(String, unique=True, index=True)
    sector_id = Column(Integer, ForeignKey("sectors.id"))
    product_description = Column(String)
    is_liked = Column(Boolean, default=False)

    sector = relationship("Sector", back_populates="companies")


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    stock_name = Column(String, nullable=False)
    stock_code = Column(String, index=True, nullable=False)
    sector_id = Column(Integer, ForeignKey("sectors.id"))
    trade_date = Column(Date, index=True, nullable=False)
    closing_price = Column(Float)
    opening_price = Column(Float)
    highest_price = Column(Float)
    lowest_price = Column(Float)
    trading_volume = Column(Integer)

    sector = relationship("Sector", back_populates="stocks")


class DailyNote(Base):
    __tablename__ = "daily_notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    note_date = Column(Date, index=True, nullable=False)
    note_title = Column(String, nullable=False)
    note_content = Column(String)

    user = relationship("User", back_populates="daily_notes")
