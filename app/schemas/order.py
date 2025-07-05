from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

# ✅ Single item for bulk order
class OrderItemIn(BaseModel):
    phone_id: int
    quantity: int

# ✅ Bulk order payload (for cart)
class OrderBulkCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str   # correct for bulk
    address: str
    total_price: float
    items: List[OrderItemIn]

# ✅ Single order for direct one phone (✅ FIXED)
class OrderCreate(BaseModel):
    model_name: str
    quantity: int
    full_name: str
    email: EmailStr
    phone_No: str   # correct for single order
    address: str
   


# ✅ Single order response
class OrderResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    phone_id: Optional[int] = None  # ✅ add for clarity
    model_name: Optional[str] = None
    quantity: Optional[int] = None
    status: str
    full_name: str
    email: EmailStr
    phone_No: str
    address: str
    reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ✅ Order summary for dashboard
class OrderSummary(BaseModel):
    total: int
    pending: int
    approved: int
    rejected: int

# ✅ Chart format
class OrderActivityResponse(BaseModel):
    date: str
    orders: int

    class Config:
        from_attributes = True

# ✅ Output list format
class OrderOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    phone_id: Optional[int] = None  # ✅ add for clarity
    model_name: Optional[str] = None
    full_name: str
    email: EmailStr
    phone_No: str
    address: str
    quantity: Optional[int] = None
    status: str
    reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ✅ Order status update
class OrderStatusUpdate(BaseModel):
    new_status: str
    reason: Optional[str] = None 