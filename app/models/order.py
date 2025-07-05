from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # ✅ Single Order only: FK to Phone
    phone_id = Column(Integer, ForeignKey("phones.id"), nullable=True)

    model_name = Column(String(255), nullable=True)  # optional for bulk
    quantity = Column(Integer, default=1)
    status = Column(String(50), default="pending")
    reason = Column(String(255), nullable=True) 
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone_No = Column(String(20), nullable=False)
    address = Column(String(255), nullable=False)

    total_price = Column(Float, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ✅ Relationships
    user = relationship("User", back_populates="orders")
    phone_obj = relationship("Phone")  # add back_populates if you define in Phone model
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")