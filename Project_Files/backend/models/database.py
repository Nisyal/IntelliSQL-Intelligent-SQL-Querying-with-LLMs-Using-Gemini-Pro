"""
SQLAlchemy database engine, session factory, base model, and ORM models.
"""

from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    Boolean,
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from config import settings

# ── Engine & Session ──────────────────────────────────────────

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before checkout
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ── Dependency for FastAPI routes ─────────────────────────────

def get_db():
    """Yield a database session and ensure it's closed after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── ORM Models ────────────────────────────────────────────────


class User(Base):
    """Registered user account."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to query history
    queries = relationship("QueryHistory", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class QueryHistory(Base):
    """Record of every NL-to-SQL query processed through the system."""

    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    natural_query = Column(Text, nullable=False)
    generated_sql = Column(Text, nullable=False)
    model_used = Column(String(100), nullable=False)
    confidence_score = Column(Float, nullable=True)
    confidence_explanation = Column(Text, nullable=True)
    results = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    executed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationship back to user
    user = relationship("User", back_populates="queries")

    def __repr__(self):
        return f"<QueryHistory(id={self.id}, model='{self.model_used}', score={self.confidence_score})>"


# ── Table creation helper ─────────────────────────────────────

def init_db():
    """Create all tables in the database. Call once at startup."""
    Base.metadata.create_all(bind=engine)
