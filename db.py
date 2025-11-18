from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Boolean, Enum, ForeignKey, Text, Numeric  
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum
from datetime import datetime
from enum import Enum as PyEnum
from .config import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


class SubscriptionStatus(enum.Enum):
    pending = "pending"
    active = "active"
    expired = "expired"
    cancelled = "cancelled"


class PaymentStatus(enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class PortfolioStatus(PyEnum):
    new = "new"
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class ContractStatus(enum.Enum):
    pending = "pending"
    active = "active"
    expired = "expired"
    cancelled = "cancelled"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    support_messages = relationship("SupportMessage", back_populates="user", cascade="all, delete-orphan")
    portfolio_contracts = relationship("PortfolioContract", back_populates="user", cascade="all, delete-orphan")



class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plan_type = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.pending)
    access_code = Column(String, nullable=True)
    code_expiry = Column(DateTime, nullable=True)
    max_uses = Column(Integer, default=1)
    used_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="subscriptions")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    card_reported = Column(String, nullable=True)
    receipt_path = Column(String, nullable=True)
    amount = Column(Integer, nullable=True)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    reviewed_by = Column(Integer, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    applied_discount = Column(Integer, nullable=True)
    applied_price = Column(Integer, nullable=True)
    invite_link = Column(String, nullable=True) 

    user = relationship("User", back_populates="payments")



class PortfolioRequest(Base):
    __tablename__ = "portfolio_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    short_agree = Column(Boolean, default=False)
    details_agree = Column(Boolean, default=False)
    message = Column(Text, nullable=True)
    admin_note = Column(Text, nullable=True)
    status = Column(Enum(PortfolioStatus), default=PortfolioStatus.new)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)

    subscription = relationship("Subscription")
    user = relationship("User")


class SupportMessage(Base):
    __tablename__ = "support_messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    responded = Column(Boolean, default=False)
    responder_admin_id = Column(Integer, nullable=True)
    response_text = Column(Text, nullable=True)
    responded_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="support_messages")


class PortfolioContract(Base):
    __tablename__ = "portfolio_contracts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    contract_number = Column(String, unique=True, index=True, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)

    amount = Column(Numeric(18, 2), nullable=False, default=0)
    currency = Column(String(3), nullable=False, default="IRR")

    status = Column(Enum(ContractStatus), default=ContractStatus.pending)

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="portfolio_contracts")
    

def init_db():
    Base.metadata.create_all(bind=engine)
