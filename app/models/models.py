from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)

    likes = relationship("Like", back_populates="user")
    dailies = relationship("Daily", back_populates="user")


class Sector(Base):
    __tablename__ = "sectors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    stocks = relationship("Stock", back_populates="sector")
    likes = relationship("Like", back_populates="sector")


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, index=True, nullable=False)
    sector_id = Column(Integer, ForeignKey("sectors.id"))
    date = Column(Date, index=True, nullable=False)
    close = Column(Float)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    volume = Column(Integer)

    sector = relationship("Sector", back_populates="stocks")


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    code = Column(String, nullable=False)
    sector_id = Column(Integer, ForeignKey("sectors.id"))

    user = relationship("User", back_populates="likes")
    sector = relationship("Sector", back_populates="likes")


class Daily(Base):
    __tablename__ = "dailies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, index=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String)

    user = relationship("User", back_populates="dailies")
