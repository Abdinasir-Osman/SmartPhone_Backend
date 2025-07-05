# routes/admin.py
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session, joinedload
from app.database import SessionLocal
from app.schemas.order import OrderActivityResponse, OrderResponse, OrderStatusUpdate
from app.utils.token import get_current_user, role_checker
from app.models.user import User
from app.models.order import Order
from app.schemas.user import UserOut
from app.controllers.order_controller import update_order_status

router = APIRouter(prefix="/admin", tags=["Admin and Super Admin"])

# ✅ DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ View all orders (with user info)
@router.get("/orders", response_model=list[OrderResponse])
def view_all_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker(["admin", "superadmin"]))
):
    return (
        db.query(Order)
        .options(joinedload(Order.user))
        .order_by(Order.created_at.desc())
        .all()
    )

# ✅ Update order status (approved/rejected) using JSON body
@router.put("/admin/orders/{order_id}/status")
def update_order_status_with_body(
    order_id: int,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker(["admin", "superadmin"]))
):
    # ❗ If rejected but no reason → error
    if payload.new_status == "rejected" and not payload.reason:
        raise HTTPException(status_code=400, detail="Reason is required for rejected orders")

    return update_order_status(
        db=db,
        order_id=order_id,
        status=payload.new_status,
        reason=payload.reason,
        current_user=current_user
    )


# ✅ Admin Profile
@router.get("/profile")
def get_admin_profile(current_user: User = Depends(role_checker(["admin", "superadmin"]))):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role
    }

# ✅ Orders Summary
@router.get("/orders/summary")
def order_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker(["admin", "superadmin"]))
):
    return {
        "total": db.query(Order).count(),
        "pending": db.query(Order).filter(Order.status == "pending").count(),
        "approved": db.query(Order).filter(Order.status == "approved").count(),
        "rejected": db.query(Order).filter(Order.status == "rejected").count(),
    }

# ✅ Orders Chart (Last 7 Days)
@router.get("/orders/activity", response_model=list[OrderActivityResponse])
def get_order_activity(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    if user.role not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Access denied")

    today = datetime.utcnow().date()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]

    results = []
    for day in last_7_days:
        count = db.query(Order).filter(
            Order.created_at >= datetime.combine(day, datetime.min.time()),
            Order.created_at <= datetime.combine(day, datetime.max.time())
        ).count()
        results.append({
            "date": day.strftime("%a"),  # eg. 'Mon', 'Tue', ...
            "orders": count
        })

    return results

# ✅ Pending Orders Count (for topbar badges etc)
@router.get("/orders/pending-count")
def get_pending_orders_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_checker(["admin", "superadmin"]))
):
    return db.query(Order).filter(Order.status == "pending").count()
