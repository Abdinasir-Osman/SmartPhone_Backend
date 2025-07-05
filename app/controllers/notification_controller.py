from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification_schema import NotificationCreate
from app.models.order import Order
import json


def create_notification(db: Session, data: NotificationCreate):
    new_notif = Notification(
        sender_id=data.sender_id,
        receiver_id=data.receiver_id,
        order_id=data.order_id,
        message=data.message,
        type=data.type,
        extra_data=json.dumps(data.extra_data) if data.extra_data else None
    )
    db.add(new_notif)
    db.commit()
    db.refresh(new_notif)
    return new_notif


def notify_admins_on_order(db: Session, sender_id: int, order_id: int, message: str, extra_data: dict = None):
    admins = db.query(User).filter(User.role.in_(["admin", "superadmin"])).all()
    for admin in admins:
        notif = Notification(
            sender_id=sender_id,
            receiver_id=admin.id,
            order_id=order_id,
            message=message,
            type="order",
            extra_data=json.dumps(extra_data) if extra_data else None
        )
        db.add(notif)
    db.commit()


def notify_on_cancelled_order(db: Session, current_user: User, order: Order, reason: str):
    admins = db.query(User).filter(User.role.in_(["admin", "superadmin"])).all()
    for admin in admins:
        notification = Notification(
            sender_id=current_user.id,
            receiver_id=admin.id,
            order_id=order.id,
            type="order_cancelled",
            title="Order Cancelled",
            message=f"Order #{order.id} was cancelled by {current_user.full_name}.",
            extra_data=json.dumps({
                "user": current_user.full_name,
                "order_id": order.id,
                "model": order.phone_model,
                "reason": reason,
            }),
        )
        db.add(notification)
    db.commit()


def get_unread_notifications(db: Session, user_id: int):
    notifs = db.query(Notification)\
        .options(
            joinedload(Notification.sender),
            joinedload(Notification.receiver),
            joinedload(Notification.order)
        )\
        .filter(
            Notification.receiver_id == user_id,
            Notification.is_read == False
        ).all()

    # ✅ Parse extra_data
    for notif in notifs:
        if isinstance(notif.extra_data, str):
            try:
                notif.extra_data = json.loads(notif.extra_data)
            except:
                notif.extra_data = {}

    return notifs


def get_all_notifications(db: Session, user_id: int):
    notifs = db.query(Notification)\
        .options(
            joinedload(Notification.sender),
            joinedload(Notification.receiver),
            joinedload(Notification.order)
        )\
        .filter(Notification.receiver_id == user_id)\
        .order_by(Notification.created_at.desc())\
        .all()

    # ✅ Parse extra_data
    for notif in notifs:
        if isinstance(notif.extra_data, str):
            try:
                notif.extra_data = json.loads(notif.extra_data)
            except:
                notif.extra_data = {}

    return notifs


def mark_notification_as_read(db: Session, notif_id: int):
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()
    return notif


def mark_all_as_read(db: Session, user_id: int):
    notifs = db.query(Notification).filter(
        Notification.receiver_id == user_id,
        Notification.is_read == False
    ).all()
    for notif in notifs:
        notif.is_read = True
    db.commit()
    return notifs
