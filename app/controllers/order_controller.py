from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.controllers.notification_controller import (
    create_notification,
    notify_on_cancelled_order
)
from app.models import user
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.phone import Phone
from app.models.user import User
from app.schemas.notification_schema import NotificationCreate
from app.utils.cbf_loader import load_cbf_data

df_features, df_images, similarity_matrix = load_cbf_data()

# ✅ SINGLE ORDER
def create_single_order(order_data, db: Session, user_id: int):
    phone = db.query(Phone).filter(Phone.model_name == order_data.model_name.strip()).first()
    if not phone:
        raise HTTPException(status_code=404, detail="Phone not found")

    df_features["model_lower"] = df_features["Model"].str.lower().str.strip()
    match_row = df_features[df_features["model_lower"] == order_data.model_name.lower().strip()]
    if match_row.empty:
        raise HTTPException(status_code=404, detail="Selling price not found in CBF dataset")

    selling_price = float(match_row["Selling Price"].values[0])
    total_price = selling_price * order_data.quantity

    order = Order(
        user_id=user_id,
        phone_id=phone.id,
        model_name=phone.model_name,
        quantity=order_data.quantity,
        full_name=order_data.full_name,
        email=order_data.email,
        phone_No=order_data.phone_No,
        address=order_data.address,
        total_price=total_price
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # ✅ Notify Admins
    admins = db.query(User).filter(User.role.in_(["admin", "superadmin"])).all()
    for admin in admins:
        create_notification(
            db,
            NotificationCreate(
                sender_id=user_id,
                receiver_id=admin.id,
                order_id=order.id,
                message="New order placed",
                type="order",
                extra_data={
                    "user": {
                        "full_name": order.full_name,
                        "email": order.email,
                        "phone": order.phone_No,
                        "address": order.address
                    },
                    "order": {
                        "model_name": order.model_name,
                        "quantity": order.quantity,
                        "order_type": "single",
                        "paid": False
                    }
                }
            )
        )
    return order


# ✅ BULK ORDER
def create_bulk_order(payload, db: Session, user_id: int):
    order = Order(
        user_id=user_id,
        full_name=payload.full_name,
        email=payload.email,
        phone_No=payload.phone,
        address=payload.address,
        total_price=payload.total_price
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    for item in payload.items:
        phone = db.query(Phone).filter(Phone.id == item.phone_id).first()
        if not phone:
            raise HTTPException(status_code=404, detail=f"Phone {item.phone_id} not found")
        order_item = OrderItem(
            order_id=order.id,
            phone_id=phone.id,
            quantity=item.quantity
        )
        db.add(order_item)

    db.commit()

    # ✅ Notify Admins
    admins = db.query(User).filter(User.role.in_(["admin", "superadmin"])).all()
    for admin in admins:
        create_notification(
            db,
            NotificationCreate(
                sender_id=user_id,
                receiver_id=admin.id,
                order_id=order.id,
                message="New order placed",
                type="order",
                extra_data={
                    "user": {
                        "full_name": order.full_name,
                        "email": order.email,
                        "phone": order.phone_No,
                        "address": order.address
                    },
                    "order": {
                        "model_name": None,
                        "quantity": None,
                        "order_type": "cart",
                        "paid": False
                    }
                }
            )
        )
    return order


# ✅ STATUS UPDATE
def update_order_status(db: Session, order_id: int, status: str, reason: str = None, current_user=None):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    order.status = status
    refund = False

    if status == "rejected":
        order.reason = reason
        if order.total_price > 0:
            refund = True
        create_notification(
            db,
            NotificationCreate(
                sender_id=current_user.id,
                receiver_id=order.user_id,
                order_id=order.id,
                message="Order rejected",
                type="reject",
                extra_data={"reason": reason, "refund": refund}
            )
        )

    elif status == "approved":
        create_notification(
            db,
            NotificationCreate(
                sender_id=current_user.id,
                receiver_id=order.user_id,
                order_id=order.id,
                message="Order approved",
                type="approve",
                extra_data={}
            )
        )

    db.commit()
    db.refresh(order)
    return order


# ✅ CANCEL ORDER FUNCTION (NEW)
def cancel_order(db: Session, order_id: int, reason: str, current_user: User):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found or not yours")

    if order.status in ["approved", "rejected", "cancelled"]:
        raise HTTPException(status_code=400, detail="Order already processed")

    order.status = "cancelled"
    order.reason = reason

    # ✅ Notify admins
    from app.controllers.notification_controller import notify_on_cancelled_order
    notify_on_cancelled_order(db, current_user, order, reason)

    db.commit()
    db.refresh(order)
    return order
