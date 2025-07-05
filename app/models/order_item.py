from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    phone_id = Column(Integer, ForeignKey("phones.id"))
    quantity = Column(Integer, default=1)

    # ✅ Relationships
    order = relationship("Order", back_populates="order_items")
    phone = relationship("Phone")
