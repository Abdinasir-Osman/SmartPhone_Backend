from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from app.controllers import order_controller
from app.database import get_db
from app.schemas.order import OrderBulkCreate, OrderCreate, OrderResponse
from app.utils.token import get_current_user, role_checker
from app.models.order import Order
from app.schemas.user import UserOut

router = APIRouter(prefix="/orders", tags=["Orders"])

# ✅ Payload for updating status with reason
class StatusUpdatePayload(BaseModel):
    status: str
    reason: Optional[str] = None

# ✅ Admin/Superadmin update order status with reason
@router.put("/{order_id}/status")
def update_status(
         order_id: int,
         payload: StatusUpdatePayload,  # { "status": "cancelled", "reason": "..." }
         db: Session = Depends(get_db),
         current_user: UserOut = Depends(role_checker(["user", "admin", "superadmin"]))
     ):
         # Hubi in user-ku leeyahay order-ka
         order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
         if not order:
             raise HTTPException(status_code=403, detail="You can only cancel your own orders.")
         # Kaliya ogolow status "cancelled" ama "deleted"
         if payload.status not in ["cancelled", "deleted"]:
             raise HTTPException(status_code=400, detail="Invalid status for user.")
         order.status = payload.status
         order.reason = payload.reason
         db.commit()
         return {"message": "Order updated successfully"}

# ✅ Admin: View All Orders
@router.get("/all", response_model=List[OrderResponse])
def get_all_orders(
    db: Session = Depends(get_db),
    current_admin: UserOut = Depends(role_checker(["admin", "superadmin"]))
):
    return db.query(Order).all()

# ✅ User: View My Orders
@router.get("/my-orders", response_model=List[OrderResponse])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    return db.query(Order).filter(Order.user_id == current_user.id).all()

# ✅ User: Filter My Orders by Status
@router.get("/my-orders/{status}", response_model=List[OrderResponse])
def get_my_orders_by_status(
    status: str,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    allowed = ["pending", "approved", "rejected"]
    if status not in allowed:
        raise HTTPException(status_code=400, detail="Invalid status filter")
    return db.query(Order).filter(
        Order.user_id == current_user.id,
        Order.status == status
    ).all()

# ✅ PLACE SINGLE ORDER (uses controller logic)
@router.post("/", response_model=OrderResponse)
def place_single_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return order_controller.create_single_order(data, db, current_user.id)

# ✅ PLACE BULK ORDER (uses controller logic)
@router.post("/bulk", response_model=OrderResponse)
def place_bulk_order(
    data: OrderBulkCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return order_controller.create_bulk_order(data, db, current_user.id)
