from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pathlib import Path as SysPath
import os

from app.database import SessionLocal
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, ChangePassword
from app.controllers.auth_controller import create_user, login_user
from app.utils.token import create_access_token, get_current_user
from app.utils.hashing import Hash

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ✅ Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Signup
@router.post("/signup", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

# ✅ Login
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    return login_user(db, user)

# ✅ Get Profile Info
@router.get("/profile", response_model=UserResponse)
def get_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

# ✅ Upload Dir
UPLOAD_DIR = "uploads/profiles"
SysPath(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

# ✅ Update Profile
@router.put("/update-profile")
def update_profile(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check duplicate email
    existing_user = db.query(User).filter(User.email == email, User.id != current_user.id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already in use")

    user = db.query(User).get(current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.full_name = full_name
    user.email = email
    user.phone = phone

    # ✅ If new file uploaded
    if file:
        file_ext = file.filename.split(".")[-1]
        file_name = f"{uuid4().hex}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, file_name)

        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        user.profile_image = f"/uploads/profiles/{file_name}"

    db.commit()
    db.refresh(user)

    return {
        "message": "Profile updated successfully",
        "user": {
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "profile_image": user.profile_image,
        }
    }

# ✅ Change Password
@router.put("/change-password")
def change_password(
    data: ChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not Hash.verify(data.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # ✅ DIB U FETCH garee user ka, si uu session local ugu noqdo
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = Hash.make(data.new_password)
    db.commit()
    db.refresh(user)

    new_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"message": "Password changed successfully", "token": new_token}