import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, validator

# ✅ User creation request schema
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    confirm_password: str  # ✅ New field

    @validator('password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in "!@#$%^&*()-_=+{}[]:;<>?/" for c in v):
            raise ValueError('Password must contain at least one special character')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

# ✅ User login request schema
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# ✅ Minimal profile view
class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr

    class Config:
        from_attributes = True

# ✅ Full user response schema
class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    status: str
    phone: Optional[str] = None
    profile_image: Optional[str] = None
    created_at: datetime.datetime

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )

# ✅ Change Password Schema
class ChangePassword(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str

# ✅ Update Profile Schema
class UpdateProfile(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    profile_image: Optional[str] = None
