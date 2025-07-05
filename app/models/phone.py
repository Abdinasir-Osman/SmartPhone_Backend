
from sqlalchemy import Column, Integer, String
from app.database import Base

class Phone(Base):
    __tablename__ = "phones"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(255), unique=True, nullable=False)
    brand = Column(String(100), nullable=False)

