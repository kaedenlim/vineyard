from sqlalchemy import create_engine, Column, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

# Create SQLite database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///./vineyard.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create declarative base
Base = declarative_base()

# Create database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Update this in database.py
class DBUser(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True)
    shopee_url = Column(String)
    lazada_url = Column(String)
    carousell_url = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo('Asia/Singapore')))
    
    # Relationships
    products = relationship("DBUserProduct", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("DBUserActivity", back_populates="user", cascade="all, delete-orphan")
    scrape_results = relationship("DBScrapeResult", back_populates="user", cascade="all, delete-orphan")

class DBUserProduct(Base):
    __tablename__ = "user_products"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String)
    price = Column(Float)
    image = Column(String)
    link = Column(String)
    site = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo('Asia/Singapore')))
    
    # Relationships
    user = relationship("DBUser", back_populates="products")

class DBUserActivity(Base):
    __tablename__ = "user_activities"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    activity = Column(String)
    timestamp = Column(DateTime, default=lambda: datetime.now(ZoneInfo('Asia/Singapore')))
    
    # Relationships
    user = relationship("DBUser", back_populates="activities")

class DBScrapeResult(Base):
    __tablename__ = "scrape_results"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_query = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(ZoneInfo('Asia/Singapore')))
    lazada_average_price = Column(Float, nullable=True)
    carousell_average_price = Column(Float, nullable=True)
    insights = Column(String, nullable=True)
    
    # Relationships
    user = relationship("DBUser", back_populates="scrape_results")
    scrape_products = relationship("DBScrapeProduct", back_populates="scrape_result", cascade="all, delete-orphan")

class DBScrapeProduct(Base):
    __tablename__ = "scrape_products"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    scrape_result_id = Column(String, ForeignKey("scrape_results.id", ondelete="CASCADE"), nullable=False)
    title = Column(String)
    price = Column(Float)
    discount = Column(Float, nullable=True)
    image = Column(String)
    link = Column(String)
    site = Column(String) 
    page_ranking = Column(Float, nullable=True)
    
    # Relationships
    scrape_result = relationship("DBScrapeResult", back_populates="scrape_products")


# Create all tables
Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 