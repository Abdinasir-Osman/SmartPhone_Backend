from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from app.controllers import payment_controller
from app.test_db import test_connection
from app.models import order
from app.database import Base, engine
from app.routes import auth, superadmin, admin, recommend, order
from app.controllers.auth_controller import create_super_admin_if_not_exists
from app.database import get_db
from app.routes.notification import router as notification_router

load_dotenv()

# ✅ Step 1: App instance
tags_metadata = [
    {"name": "Super Admin", "description": "Manage roles and user privileges"},
    {"name": "Authentication", "description": "User signup/login functionality"},
    {"name": "Recommendation", "description": "Phone recommendation engine"},
]

app = FastAPI(title="Smartphone Recommendation API", openapi_tags=tags_metadata)

# ✅ Step 2: CORS Middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://172.29.180.34:5173",   # IP-ga PC-gaaga
        "http://10.0.2.2:5173",        # Android emulator
        "http://localhost:19001",      # Expo web
        "http://10.184.186.34:19006",  # Expo web dev
        "exp://10.184.186.34:19000",   # Expo Go mobile
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ Step 3: DB Tables
Base.metadata.create_all(bind=engine)

# ✅ Step 4: Routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(superadmin.router)
app.include_router(recommend.router)
app.include_router(order.router)
app.include_router(payment_controller.router)
app.include_router(notification_router)

# ✅ Step 4.1: Static files (uploads)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ✅ Step 5: DB Connection Test
test_connection()

# ✅ Step 6: Create superadmin
@app.on_event("startup")
def startup_event():
    db = next(get_db())
    create_super_admin_if_not_exists(db)

# ✅ Step 7: Root
@app.get("/")
def read_root():
    return {"message": "Welcome to the Smartphone Recommender API"}
