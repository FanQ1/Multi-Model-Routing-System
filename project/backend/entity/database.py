
from sqlalchemy import UUID, create_engine, Column, String, Integer, JSON, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from settings import Settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

SQLALCHEMY_DATABASE_URL = Settings().get_postgresql_url()
ASYNC_SQLALCHEMY_DATABASE_URL = Settings().get_async_postgresql_url()

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# async engine
async_engine = create_async_engine(ASYNC_SQLALCHEMY_DATABASE_URL)
async_session_maker = async_sessionmaker(
    async_engine, 
    class_=AsyncSession,
    expire_on_commit=False
)

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

# user
class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)

# ==================memory related records========================
class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID, primary_key=True, index=True)
    message_type = Column(String, index=True)  # user or assistant
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID, primary_key=True, index=True)
    conversation_summary = Column(Text)
    last_updated = Column(DateTime, default=datetime.utcnow)

class ConversationMessageLink(Base):
    # one conversation can have multiple messages
    __tablename__ = "conversation_message_links"

    id = Column(UUID, primary_key=True, index=True)
    conversation_id = Column(UUID, index=True)
    message_id = Column(UUID, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ConversationUserLink(Base):
    # one user can have multiple conversations
    __tablename__ = "conversation_user_links"

    id = Column(UUID, primary_key=True, index=True)
    conversation_id = Column(UUID, index=True)
    user_id = Column(UUID, index=True)



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
