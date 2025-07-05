import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database import SessionLocal
from app.models.user import User
from app.models.order import Order
from app.models.phone import Phone
from app.schemas.user import UserOut, UserResponse
from app.utils.token import role_checker
from typing import Optional
import csv
import io

router = APIRouter(prefix="/super", tags=["Super Admin"])

# ✅ DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ View All Users (With Search, Filter)
@router.get("/users", response_model=list[UserResponse])
def view_all_users(
    search: str = "",
    role: str = "",
    status: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker(["superadmin"]))
):
    query = db.query(User)

    if search:
        query = query.filter(
            (User.full_name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )

    if role:
        query = query.filter(User.role == role)

    if status:
        query = query.filter(User.status == status)

    return query.order_by(User.created_at.desc()).all()

# ✅ Export Users as CSV
@router.get("/users/export")
def export_users_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker(["superadmin"]))
):
    users = db.query(User).filter(User.role != "superadmin").order_by(User.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Full Name", "Email", "Role", "Status", "Created At"])

    for user in users:
        writer.writerow([
            user.id,
            user.full_name,
            user.email,
            user.role,
            user.status,
            user.created_at.strftime("%Y-%m-%d %H:%M:%S")
        ])

    filename = f"users-{datetime.date.today().strftime('%Y-%m-%d')}.csv"
    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response

# ✅ Toggle User Status (Active/Inactive)
@router.patch("/toggle-status/{user_id}")
def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker(["superadmin"]))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.status = "inactive" if user.status == "active" else "active"
    db.commit()
    return {
        "success": True,
        "message": f"{user.full_name}'s status changed to {user.status}"
    }

# ✅ Promote User to Admin
@router.put("/promote/{user_id}")
def promote_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker(["superadmin"]))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = "admin"
    db.commit()
    return {
        "success": True,
        "message": f"{user.full_name} promoted to admin"
    }

# ✅ Demote Admin to User
@router.put("/demote/{user_id}")
def demote_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker(["superadmin"]))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.role != "admin":
        raise HTTPException(status_code=400, detail="Not an admin")

    user.role = "user"
    db.commit()
    return {
        "success": True,
        "message": f"{user.full_name} demoted to user"
    }

# ✅ View Admins Only
@router.get("/active-admins", response_model=list[UserOut])
def view_active_admins(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker(["superadmin"]))
):
    return db.query(User).filter(User.role == "admin").all()

# ✅ Analytics Summary
@router.get("/analytics/summary")
def analytics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker(["superadmin"]))
):
    total_users = db.query(User).filter(User.role != "superadmin").count()
    total_orders = db.query(Order).count()
    total_revenue = db.query(func.sum(Order.total_price)).scalar() or 0

    return {
        "total_users": total_users,
        "total_orders": total_orders,
        "total_revenue": total_revenue
    }

# ✅ User Status Distribution
@router.get("/analytics/user-status")
def user_status_chart(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker(["superadmin"]))
):
    active = db.query(User).filter(User.status == "active", User.role != "superadmin").count()
    inactive = db.query(User).filter(User.status == "inactive", User.role != "superadmin").count()

    return {"active": active, "inactive": inactive}

# ✅ Orders Trend (Weekly)
@router.get("/analytics/orders-trend")
def orders_trend(
    range: str = Query("weekly", enum=["weekly"]),
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker(["superadmin"]))
):
    today = datetime.date.today()
    week_ago = today - datetime.timedelta(days=6)

    result = (
        db.query(func.date(Order.created_at).label("date"), func.count().label("count"))
        .filter(Order.created_at >= week_ago)
        .group_by(func.date(Order.created_at))
        .order_by("date")
        .all()
    )

    return [{"date": str(row.date), "count": row.count} for row in result]

# ✅ Top 5 Ordered Phones
@router.get("/analytics/top-phones")
def top_phones(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker(["superadmin"]))
):
    results = (
        db.query(Phone.model_name, func.count(Order.id).label("orders"))
        .join(Order, Phone.id == Order.phone_id)
        .group_by(Phone.model_name)
        .order_by(desc("orders"))
        .limit(5)
        .all()
    )

    return [{"model_name": model, "orders": count} for model, count in results]
