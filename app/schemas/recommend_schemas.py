from pydantic import BaseModel
from typing import Optional

class PhoneOut(BaseModel):
    Brand: str
    Model: str
    RAM: str
    Storage: str
    Rating: float
    Price: float
    Image_URL: str
    similarity: Optional[float] = None
    formatted_message: Optional[str] = None  # ✅ Xalka muhiimka ah

    class Config:
        from_attributes = True
