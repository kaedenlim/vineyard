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


# Create all tables
Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 