from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.database import SessionLocal
from app.models import Tenant, Payment, Unit, Expense

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_dashboard(db: Session = Depends(get_db)):

    total_tenants = db.query(Tenant).count()

    total_payments = db.query(Payment).count()

    total_revenue = db.query(func.sum(Payment.amount)).scalar() or 0

    return {
        "total_tenants": total_tenants,
        "total_payments": total_payments,
        "total_revenue": total_revenue
    }
    
def get_financial_report(db):

    total_rent_collected = (
        db.query(func.sum(Payment.amount)).scalar() or 0
    )

    total_expenses = (
        db.query(func.sum(Expense.amount)).scalar() or 0
    )

    net_profit = total_rent_collected - total_expenses

    total_units = db.query(Unit).count()

    occupied_units = db.query(Unit).filter(
        Unit.status == "Occupied"
    ).count()

    occupancy_rate = (
        (occupied_units / total_units) * 100
        if total_units > 0 else 0
    )

    outstanding_rent = (
        db.query(func.sum(Tenant.balance)).scalar() or 0
    )

    current_month = datetime.now().month
    current_year = datetime.now().year

    monthly_revenue = (
        db.query(func.sum(Payment.amount))
        .filter(
            func.extract("month", Payment.payment_date) == current_month,
            func.extract("year", Payment.payment_date) == current_year
        )
        .scalar() or 0
    )

    return {
        "total_rent_collected": total_rent_collected,
        "total_expenses": total_expenses,
        "net_profit": net_profit,
        "occupancy_rate": round(occupancy_rate, 2),
        "outstanding_rent": outstanding_rent,
        "monthly_revenue": monthly_revenue
    }