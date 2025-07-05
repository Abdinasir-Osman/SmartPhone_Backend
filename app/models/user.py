from sqlalchemy import Column, Integer, String, func
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy import DateTime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    password = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    status = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())  
    profile_image = Column(String(255), nullable=True) 
    
    # ✅ Relationship to orders
    orders = relationship("Order", back_populates="user")
