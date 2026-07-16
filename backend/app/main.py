from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import dashboard
from datetime import datetime
from dateutil.relativedelta import relativedelta
from app.database import engine, Base, get_db
from app import models, schemas, crud, security
from app import pdf_generator
from fastapi.responses import FileResponse



app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "Rental System Backend Running 🚀"}

@app.post("/tenants", response_model=schemas.TenantResponse)
def create_tenant(
    tenant: schemas.TenantCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(security.verify_token)
):
    return crud.create_tenant(db, tenant)

@app.get("/tenants")
def get_tenants(
    db: Session = Depends(get_db),
    current_user: str = Depends(security.verify_token)
):
    return crud.get_tenants(db)

@app.get(
    "/tenants/{tenant_id}/statement",
    response_model=schemas.TenantStatement
)
def tenant_statement(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(security.verify_token)
):
    return crud.get_tenant_statement(db, tenant_id)

@app.post(
    "/payments",
    response_model=schemas.PaymentResponse
)
def create_payment(
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(security.verify_token)
):
   

    return crud.create_payment(db, payment)

@app.get(
    "/payments",
    response_model=list[schemas.PaymentResponse]
)
def get_payments(
    db: Session = Depends(get_db),
    current_user: str = Depends(security.verify_token)
):
    return crud.get_payments(db)


@app.post(
    "/units",
    response_model=schemas.UnitResponse
)
def create_unit(
    unit: schemas.UnitCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(security.verify_token)
):
    return crud.create_unit(db, unit)


@app.get(
    "/units",
    response_model=list[schemas.UnitResponse]
)
def get_units(
    db: Session = Depends(get_db),
    current_user: str = Depends(security.verify_token)
):
    return crud.get_units(db)


@app.get(
    "/units/{unit_id}",
    response_model=schemas.UnitResponse
)
def get_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(security.verify_token)
):
    return crud.get_unit(db, unit_id)


@app.post(
    "/register",
    response_model=schemas.UserResponse
)
def register_admin(
    admin: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    existing = crud.get_user_by_username(
        db,
        admin.username
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    admin.role = "admin"

    return crud.create_user(
        db,
        admin
    )
    
@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = crud.authenticate_user(
        db,
        form_data.username,
        form_data.password
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

    access_token = security.create_access_token(

        {

            "sub": user.username,

            "id": user.id,

            "role": user.role,

            "tenant_id": user.tenant_id

        }

    )

    return {

        "access_token": access_token,

        "token_type": "bearer",

        "role": user.role

    }
    
@app.post(
    "/users",
    response_model=schemas.UserResponse
)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):

    existing = crud.get_user_by_username(
        db,
        user.username
    )

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    return crud.create_user(
        db,
        user
    )

@app.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):

    total_units = db.query(models.Unit).count()

    occupied_units = db.query(models.Unit).filter(
        models.Unit.status == "Occupied"
    ).count()

    vacant_units = db.query(models.Unit).filter(
        models.Unit.status == "Vacant"
    ).count()

    occupancy_rate = (
        (occupied_units / total_units) * 100
        if total_units > 0 else 0
    )

    expected_monthly_income = db.query(
        func.sum(models.Unit.rent_amount)
    ).filter(
        models.Unit.status == "Occupied"
    ).scalar() or 0

    unpaid_tenants = db.query(models.Tenant).filter(
        models.Tenant.balance > 0
    ).count()

    return {
        "total_units": total_units,
        "occupied_units": occupied_units,
        "vacant_units": vacant_units,
        "occupancy_rate": round(occupancy_rate, 2),
        "expected_monthly_income": expected_monthly_income,
        "unpaid_tenants": unpaid_tenants
    }
    
@app.post("/run-billing")
def run_billing(db: Session = Depends(get_db)):
    billed_count = crud.apply_monthly_billing(db)

    return {
        "message": "Monthly billing updated",
        "tenants_billed": billed_count
    }
    
@app.get("/tenants/overdue")
def get_overdue_tenants(db: Session = Depends(get_db)):

    tenants = db.query(models.Tenant).filter(
        models.Tenant.balance > 0
    ).all()

    return [
        {
            "id": t.id,
            "name": t.name,
            "phone": t.phone,
            "monthly_rent": t.monthly_rent,
            "balance": t.balance,
            "months_owing": round(t.balance / t.monthly_rent, 1)
        }
        for t in tenants
    ]
    
@app.put(
    "/tenants/{tenant_id}/renew",
    response_model=schemas.TenantResponse
)
def renew_lease(
    tenant_id: int,
    lease: schemas.LeaseRenew,
    db: Session = Depends(get_db),
    current_user: str = Depends(security.verify_token)
):
    return crud.renew_lease(
        db,
        tenant_id,
        lease.lease_start,
        lease.lease_end
    )
    
@app.post("/leases/check-expired")
def check_expired_leases(
    db: Session = Depends(get_db),
    current_user: str = Depends(security.verify_token)
):
    updated = crud.update_expired_leases(db)

    return {
        "expired_leases": updated
    }
    
@app.post("/tenants/{tenant_id}/checkout")
def checkout_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(security.verify_token)
):
    return crud.checkout_tenant(db, tenant_id)

@app.post(
    "/expenses",
    response_model=schemas.ExpenseResponse
)
def create_expense(
    expense: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(security.verify_token)
):
    return crud.create_expense(db, expense)


@app.get(
    "/expenses",
    response_model=list[schemas.ExpenseResponse]
)
def get_expenses(
    db: Session = Depends(get_db),
    current_user: str = Depends(security.verify_token)
):
    return crud.get_expenses(db)

@app.get("/reports/financial")
def financial_report(
    db: Session = Depends(get_db),
    current_user: str = Depends(security.verify_token)
):
    return dashboard.get_financial_report(db)

@app.get("/payments/{payment_id}/receipt/pdf")
def download_receipt(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(security.verify_token)
):

    receipt = crud.get_receipt(db, payment_id)

    pdf = pdf_generator.generate_receipt(receipt)

    return FileResponse(
        pdf,
        media_type="application/pdf",
        filename=f"{receipt['receipt_number']}.pdf"
    )
    
@app.post("/notifications", response_model=schemas.NotificationResponse)
def create_notification(
    notification: schemas.NotificationCreate,
    db: Session = Depends(get_db)
):
    return crud.create_notification(db, notification)

@app.get("/notifications", response_model=list[schemas.NotificationResponse])
def get_notifications(db: Session = Depends(get_db)):
    return crud.get_notifications(db)

@app.get("/notifications/unread/count")
def unread_notification_count(db: Session = Depends(get_db)):
    count = crud.get_unread_notification_count(db)

    return {
        "unread_notifications": count
    }
    
@app.get("/notifications/{tenant_id}", response_model=list[schemas.NotificationResponse])
def get_notifications_by_tenant(
    tenant_id: int,
    db: Session = Depends(get_db)
):
    return crud.get_notifications_by_tenant(db, tenant_id)

@app.patch("/notifications/{notification_id}/read",
           response_model=schemas.NotificationResponse)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    notification = crud.mark_notification_as_read(db, notification_id)

    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")

    return notification

