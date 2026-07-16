from app.database import Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    house_number = Column(String)
    
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True)
    
    monthly_rent = Column(Float)
    balance = Column(Float, default=0)
    
    last_billed_date = Column(DateTime, nullable=True)
    
    lease_start = Column(Date, nullable=True)
    lease_end = Column(Date, nullable=True)
    deposit = Column(Float, default=0)
    lease_status = Column(String, default="Active")
    
    checkout_date = Column(Date, nullable=True)
    
    unit = relationship("Unit", back_populates="tenants")
    payments = relationship("Payment", back_populates="tenant")
    user = relationship("User", back_populates="tenant", uselist=False)
    notifications = relationship("Notification", back_populates="tenant")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    amount = Column(Float)

    payment_date = Column(
        DateTime(timezone=True),
        server_default=func.now()
   
    )
    receipt_number = Column(String, unique=True, index=True)
    payment_method = Column(String, default="Cash")
    transaction_reference = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    tenant = relationship("Tenant", back_populates="payments")
    
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant", back_populates="notifications")

    
class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    unit_number = Column(String, unique=True, index=True)
    rent_amount = Column(Float)
    status = Column(String, default="Vacant")
    
    tenants = relationship("Tenant", back_populates="unit")
    
class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    description = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    expense_date = Column(DateTime(timezone=True), server_default=func.now())
    
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, nullable=False)

    email = Column(String, unique=True, nullable=False)

    hashed_password = Column(String, nullable=False)

    role = Column(String, default="tenant")

    tenant_id = Column(
        Integer,
        ForeignKey("tenants.id"),
        nullable=True
    )

    is_active = Column(Boolean, default=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    tenant = relationship("Tenant", back_populates="user")