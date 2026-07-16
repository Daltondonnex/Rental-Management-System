from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from pydantic import EmailStr

class TenantCreate(BaseModel):
    name: str
    phone: str
    house_number: str
    unit_id: int | None = None
    monthly_rent: float
    
    lease_start: date | None = None
    lease_end: date | None = None
    deposit: float | None = 0

class TenantResponse(TenantCreate):
    id: int
    balance: float
    lease_status: str

    class Config:
        from_attributes = True
        
class PaymentCreate(BaseModel):
    tenant_id: int
    amount: float
    payment_method: str = "Cash"
    transaction_reference: str | None = None
    notes: str | None = None

class PaymentResponse(BaseModel):
    id: int
    tenant_id: int
    amount: float
    payment_date: datetime
    receipt_number: str

    class Config:
        from_attributes = True


class PaymentHistory(BaseModel):
    amount: float
    payment_date: datetime

    class Config:
        from_attributes = True


class TenantStatement(BaseModel):
    tenant_id: int
    tenant_name: str
    phone: str
    unit_number: str | None = None
    monthly_rent: float
    current_balance: float
    total_paid: float
    total_outstanding: float
    months_owing: float
    payments: list[PaymentHistory]
 
class Token(BaseModel):
    access_token: str
    token_type: str
    
    # -------------------------
# Unit Schemas
# -------------------------

class UnitCreate(BaseModel):
    unit_number: str
    rent_amount: float


class UnitResponse(UnitCreate):
    id: int
    status: str

    class Config:
        from_attributes = True
        
class LeaseRenew(BaseModel):
    lease_start: date
    lease_end: date


class ExpenseCreate(BaseModel):
    category: str
    description: str | None = None
    amount: float


class ExpenseResponse(ExpenseCreate):
    id: int
    expense_date: datetime

    class Config:
        from_attributes = True
        
class UserBase(BaseModel):
    username: str
    email: EmailStr
    
class UserCreate(UserBase):
    password: str
    role: str = "tenant"
    tenant_id: Optional[int] = None
    
class UserLogin(BaseModel):
    username: str
    password: str
    
class UserResponse(UserBase):
    id: int
    role: str
    tenant_id: Optional[int]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
    
class NotificationCreate(BaseModel):
    tenant_id: int
    message: str


class NotificationResponse(BaseModel):
    id: int
    tenant_id: int
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True