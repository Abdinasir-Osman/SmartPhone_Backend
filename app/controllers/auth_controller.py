from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# ✅ Schema Imports
from app.models.order_item import OrderItem
from app.schemas.order import OrderOut
from app.schemas.user import UserCreate, UserLogin, UserOut

# ✅ Utility Imports
from app.utils.hashing import Hash
from app.utils.token import create_access_token, get_current_user
from app.database import get_db
from app.models.order import Order
from app.models.user import User

# ✅ Router Object with Tags
router = APIRouter(tags=["Admin and Super Admin"])

# ✅ User Registration
def create_user(db: Session, user_data: UserCreate):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # ✅ Check confirm_password
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    hashed_password = Hash.make(user_data.password)
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password=hashed_password,
        role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ✅ Login Logic
def login_user(db: Session, login_data: UserLogin):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Invalid credentials")
    if not Hash.verify(login_data.password, user.password):
        raise HTTPException(status_code=403, detail="Incorrect password")

    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {
        "token": access_token,        # ✅ frontend expects "token" not access_token
        "role": user.role,
        "email": user.email,
        "full_name": user.full_name
    }


# ✅ Auto-create Superadmin
def create_super_admin_if_not_exists(db: Session):
    existing = db.query(User).filter(User.email == "abdinasir@system.com").first()
    if not existing:
        super_admin = User(
            full_name="Abdinasir Osman Warsame",
            email="abdinasir@system.com",
            password=Hash.make("Abdi@12345"),
            role="superadmin"
        )
        db.add(super_admin)
        db.commit()

# ✅ Get Admin Profile
@router.get("/admin/profile", response_model=UserOut)
def get_admin_profile(user=Depends(get_current_user)):
    if user.role not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return user

# ✅ Get All Orders
@router.get("/admin/orders", response_model=list[OrderOut])
def view_all_orders(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.role not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return db.query(Order).order_by(Order.created_at.desc()).all()



