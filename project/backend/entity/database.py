
from sqlalchemy import create_engine, Column, String, Integer, JSON, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from ..settings import Settings

SQLALCHEMY_DATABASE_URL = Settings().get_postgresql_url()

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Model(Base):
    __tablename__ = "models"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    capability_ranks = Column(JSON)  # 存储原始排名
    capability_vector = Column(JSON)  # 存储能力向量（一维数组）

    max_tokens = Column(Integer, nullable=True, default=8192)
    avg_latency_ms = Column(Integer, nullable=True, default=1000)
    cost_per_1k_usd = Column(Float, nullable=True, default=0.01)
    stake_eth = Column(Float, nullable=True, default=10.0)
    is_verified = Column(Boolean, default=False)
    trust_score = Column(Float, default=50.0)
    violations = Column(Integer, default=0)
    registration_time = Column(DateTime, default=datetime.utcnow)

class RoutingRecord(Base):
    __tablename__ = "routing_records"

    id = Column(String, primary_key=True, index=True)
    model_id = Column(String, index=True)
    model_name = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_query = Column(Text)
    selected_reason = Column(String)

class PerformanceRecord(Base):
    __tablename__ = "performance_records"

    id = Column(String, primary_key=True, index=True)
    model_id = Column(String, index=True)
    period = Column(String)
    avg_latency_ms = Column(Integer)
    success_rate = Column(Float)
    uptime_percentage = Column(Float)
    violations = Column(Integer, default=0)
    report_time = Column(DateTime, default=datetime.utcnow)

class ViolationRecord(Base):
    __tablename__ = "violation_records"

    id = Column(String, primary_key=True, index=True)
    model_id = Column(String, index=True)
    issue = Column(Text)
    severity = Column(String)
    slash_amount_eth = Column(Float)
    report_time = Column(DateTime, default=datetime.utcnow)

# Database initialization
def init_db():
    """Initialize the database by creating all tables"""
    Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    """FastAPI dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
