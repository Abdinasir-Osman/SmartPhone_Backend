from pydantic import BaseModel
from datetime import datetime

class SenderReceiverInfo(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str | None = None
    address: str | None = None
    profile_image: str | None = None  # ✅ Added here

    class Config:
        orm_mode = True

class OrderInfo(BaseModel):
    id: int
    model_name: str
    quantity: int | None = None
    order_type: str | None = None
    paid: bool | None = None

    class Config:
        orm_mode = True

class NotificationCreate(BaseModel):
    sender_id: int
    receiver_id: int
    order_id: int | None = None
    message: str
    type: str  # 'order', 'approve', 'reject', 'update'
    extra_data: dict | None = None

class NotificationOut(BaseModel):
    id: int
    sender: SenderReceiverInfo
    receiver: SenderReceiverInfo
    order: OrderInfo | None = None
    message: str
    type: str
    extra_data: dict | None = None
    is_read: bool
    created_at: datetime

    class Config:
        orm_mode = True
