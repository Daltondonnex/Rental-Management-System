from fastapi import HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, security
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sqlalchemy import func
import uuid
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def create_tenant(db: Session, tenant: schemas.TenantCreate):
    db_tenant = models.Tenant(
        name=tenant.name,
        phone=tenant.phone,
        house_number=tenant.house_number,
        unit_id=tenant.unit_id,
        monthly_rent=tenant.monthly_rent,
        balance=tenant.monthly_rent,
        lease_start=tenant.lease_start,
        lease_end=tenant.lease_end,
        deposit=tenant.deposit,
        lease_status="Active"
    )
    
    if tenant.unit_id:
        unit = db.query(models.Unit).filter(
            models.Unit.id == tenant.unit_id
        ).first()

        if unit:
            unit.status = "Occupied"

    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)

    return db_tenant

def get_tenants(db: Session):
    return db.query(models.Tenant).all()

def create_payment(db: Session, payment: schemas.PaymentCreate):

    tenant = db.query(models.Tenant).filter(
        models.Tenant.id == payment.tenant_id
    ).first()

    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant not found"
        )

    receipt_number = f"RCT-{uuid.uuid4().hex[:8].upper()}"

    db_payment = models.Payment(
        tenant_id=payment.tenant_id,
        amount=payment.amount,
        receipt_number=receipt_number,
        payment_method=payment.payment_method,
        transaction_reference=payment.transaction_reference,
        notes=payment.notes
    )

    tenant.balance -= payment.amount

    if tenant.balance < 0:
        tenant.balance = 0
    
    notification = models.Notification(
    tenant_id=payment.tenant_id,
    message=f"Payment of KSh {payment.amount} received successfully."
)

    db.add(notification)
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    return db_payment


def get_tenant_statement(db: Session, tenant_id: int):

    tenant = db.query(models.Tenant).filter(
        models.Tenant.id == tenant_id
    ).first()

    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant not found"
        )

    payments = db.query(models.Payment).filter(
        models.Payment.tenant_id == tenant_id
    ).order_by(
        models.Payment.payment_date.desc()
    ).all()

    total_paid = db.query(
        func.sum(models.Payment.amount)
    ).filter(
        models.Payment.tenant_id == tenant_id
    ).scalar() or 0

    unit_number = None

    if tenant.unit:
        unit_number = tenant.unit.unit_number

    months_owing = 0

    if tenant.monthly_rent > 0:
        months_owing = round(
            tenant.balance / tenant.monthly_rent,
            1
        )

    return {
        "tenant_id": tenant.id,
        "tenant_name": tenant.name,
        "phone": tenant.phone,
        "unit_number": unit_number,
        "monthly_rent": tenant.monthly_rent,
        "current_balance": tenant.balance,
        "total_paid": total_paid,
        "total_outstanding": tenant.balance,
        "months_owing": months_owing,
        "payments": payments
    }

def get_payments(db: Session):
    return db.query(models.Payment).order_by(
        models.Payment.payment_date.desc()
    ).all()


def get_dashboard(db: Session):
    total_tenants = db.query(models.Tenant).count()

    total_payments = db.query(models.Payment).count()

    total_revenue = (
        db.query(func.sum(models.Payment.amount)).scalar() or 0
    )

    return {
        "total_tenants": total_tenants,
        "total_payments": total_payments,
        "total_revenue": total_revenue
    }



def login_admin(db: Session, form_data):

    db_admin = db.query(models.Admin).filter(
        models.Admin.username == form_data.username
    ).first()

    if not db_admin:
        return None

    if not security.verify_password(
        form_data.password,
        db_admin.hashed_password
    ):
        return None

    access_token = security.create_access_token(
        data={"sub": db_admin.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
    
    # =========================
# UNIT CRUD
# =========================

def create_unit(db: Session, unit: schemas.UnitCreate):

    db_unit = models.Unit(
        unit_number=unit.unit_number,
        rent_amount=unit.rent_amount
    )

    db.add(db_unit)
    db.commit()
    db.refresh(db_unit)

    return db_unit


def get_units(db: Session):
    return db.query(models.Unit).all()


def get_unit(db: Session, unit_id: int):
    return db.query(models.Unit).filter(
        models.Unit.id == unit_id
    ).first()


def update_unit_status(db: Session, unit_id: int, status: str):

    unit = db.query(models.Unit).filter(
        models.Unit.id == unit_id
    ).first()

    if unit:
        unit.status = status
        db.commit()
        db.refresh(unit)

    return unit

def apply_monthly_billing(db: Session):

    tenants = db.query(models.Tenant).all()
    today = datetime.utcnow()

    billed_count = 0

    for tenant in tenants:

        if not tenant.last_billed_date:
            tenant.last_billed_date = today
            continue

        next_bill_date = tenant.last_billed_date + relativedelta(months=1)

        if today >= next_bill_date:

            tenant.balance += tenant.monthly_rent
            tenant.last_billed_date = today
            billed_count += 1

    db.commit()

    return billed_count

def renew_lease(
    db: Session,
    tenant_id: int,
    lease_start: date,
    lease_end: date
):

    tenant = db.query(models.Tenant).filter(
        models.Tenant.id == tenant_id
    ).first()

    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant not found"
        )

    tenant.lease_start = lease_start
    tenant.lease_end = lease_end
    tenant.lease_status = "Active"

    db.commit()
    db.refresh(tenant)

    return tenant


def update_expired_leases(db: Session):

    today = date.today()

    tenants = db.query(models.Tenant).all()

    updated = 0

    for tenant in tenants:

        if (
            tenant.lease_end
            and tenant.lease_end < today
            and tenant.lease_status == "Active"
        ):

            tenant.lease_status = "Expired"
            updated += 1

    db.commit()

    return updated

def checkout_tenant(db: Session, tenant_id: int):

    tenant = db.query(models.Tenant).filter(
        models.Tenant.id == tenant_id
    ).first()

    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant not found"
        )

    if tenant.balance > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Tenant has an outstanding balance of {tenant.balance}"
        )

    if tenant.unit:
        tenant.unit.status = "Vacant"

    tenant.lease_status = "Terminated"
    tenant.checkout_date = date.today()

    db.commit()

    return {
        "message": "Tenant checked out successfully",
        "tenant": tenant.name,
        "unit": tenant.unit.unit_number if tenant.unit else None,
        "checkout_date": tenant.checkout_date
    }
    
def create_expense(db: Session, expense: schemas.ExpenseCreate):

    db_expense = models.Expense(
        category=expense.category,
        description=expense.description,
        amount=expense.amount
    )

    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)

    return db_expense


def get_expenses(db: Session):

    return db.query(models.Expense).order_by(
        models.Expense.expense_date.desc()
    ).all()
    
def get_receipt(db: Session, payment_id: int):

    payment = (
        db.query(models.Payment)
        .filter(models.Payment.id == payment_id)
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    tenant = payment.tenant

    return {
    "receipt_number": payment.receipt_number,
    "tenant_name": tenant.name,
    "unit_number": tenant.unit.unit_number if tenant.unit else tenant.house_number,
    "amount_paid": payment.amount,
    "payment_date": payment.payment_date.strftime("%d %B %Y %I:%M %p"),
    "remaining_balance": tenant.balance,
    "payment_method": payment.payment_method,
    "transaction_reference": payment.transaction_reference,
    "notes": payment.notes
}
    
def hash_password(password: str):

    return pwd_context.hash(password)

def verify_password(
    plain_password,
    hashed_password
):

    return pwd_context.verify(
        plain_password,
        hashed_password
    )
    
def create_user(
    db: Session,
    user: schemas.UserCreate
):

    db_user = models.User(

        username=user.username,

        email=user.email,

        hashed_password=hash_password(
            user.password
        ),

        role=user.role,

        tenant_id=user.tenant_id

    )

    db.add(db_user)

    db.commit()

    db.refresh(db_user)

    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(
        models.User.username == username
    ).first()

def authenticate_user(
    db: Session,
    username: str,
    password: str
):

    user = get_user_by_username(
        db,
        username
    )

    if not user:

        return None

    if not verify_password(
        password,
        user.hashed_password
    ):

        return None

    return user

def create_notification(db, notification: schemas.NotificationCreate):
    new_notification = models.Notification(
        tenant_id=notification.tenant_id,
        message=notification.message
    )

    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    return new_notification


def get_notifications(db):
    return db.query(models.Notification).all()


def get_notifications_by_tenant(db, tenant_id: int):
    return (
        db.query(models.Notification)
        .filter(models.Notification.tenant_id == tenant_id)
        .all()
    )


def mark_notification_as_read(db, notification_id: int):
    notification = (
        db.query(models.Notification)
        .filter(models.Notification.id == notification_id)
        .first()
    )

    if notification:
        notification.is_read = True
        db.commit()
        db.refresh(notification)

    return notification

def get_unread_notification_count(db):
    return (
        db.query(models.Notification)
        .filter(models.Notification.is_read == False)
        .count()
    )