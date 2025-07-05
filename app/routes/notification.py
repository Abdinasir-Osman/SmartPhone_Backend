# app/routers/notification.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.controllers.notification_controller import (
    create_notification,
    get_unread_notifications,
    get_all_notifications,
    mark_notification_as_read,
    mark_all_as_read
)
from app.database import get_db
from app.schemas.notification_schema import NotificationCreate, NotificationOut

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# ✅ Send a manual notification (if needed)
@router.post("/", response_model=NotificationOut)
def send_notification(
    data: NotificationCreate,
    db: Session = Depends(get_db)
):
    return create_notification(db, data)

# ✅ Get unread notifications for specific user
@router.get("/unread/{user_id}", response_model=List[NotificationOut])
def get_unread(
    user_id: int,
    db: Session = Depends(get_db)
):
    return get_unread_notifications(db, user_id)

# ✅ Get all notifications (ordered) for user
@router.get("/all/{user_id}", response_model=List[NotificationOut])
def get_all(
    user_id: int,
    db: Session = Depends(get_db)
):
    return get_all_notifications(db, user_id)

# ✅ Mark a single notification as read
@router.put("/{notif_id}/read", response_model=NotificationOut)
def read_notification(
    notif_id: int,
    db: Session = Depends(get_db)
):
    return mark_notification_as_read(db, notif_id)

# ✅ Mark all notifications for a user as read
@router.put("/all/{user_id}/read", response_model=List[NotificationOut])
def read_all(
    user_id: int,
    db: Session = Depends(get_db)
):
    return mark_all_as_read(db, user_id)
