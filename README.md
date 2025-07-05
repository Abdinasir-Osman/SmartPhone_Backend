# 📱 Smartphone Recommendation Backend API

This is a complete backend system for a smartphone e-commerce and recommendation platform, developed using **FastAPI**, **SQLAlchemy**, and **MySQL**.

It includes user management, order handling, AI-powered recommendations, and admin/superadmin analytics. Swagger docs are auto-generated and can be accessed at `/docs`.

---

## 🔧 Features

- 🔐 **Authentication**
  - JWT-based login and registration
  - Admin & user role control

- 🧑‍💼 **Role-Based Access**
  - Super Admin manages all users and orders
  - Branch Admin manages specific data

- 📱 **Recommendation Engine**
  - Content-Based Filtering (CBF)
  - Collaborative Filtering (CF)
  - Hybrid Recommendation

- 🛒 **Order System**
  - Place, view, approve/reject orders
  - Track order status

- 📊 **Analytics**
  - Total users, orders, revenue
  - Activity charts

- 📩 **Notifications**
  - GET all notifications
  - GET by user
  - POST send notification to all or specific user

- 💬 **Default Route**
  - Health check: `/` shows system status

---

## 📚 API Categories

| Category        | Description                           |
|----------------|---------------------------------------|
| `/auth/`        | Authentication (register, login)      |
| `/users/`       | User management by Admins             |
| `/orders/`      | Order handling                        |
| `/recommend/`   | Recommendation system endpoints       |
| `/analytics/`   | Summary data for admins               |
| `/notifications/` | Send and retrieve alerts             |
| `/`             | Default route - system running check  |

---

## 🚀 Getting Started

### 🔗 Requirements:
- Python 3.10+
- MySQL
- virtualenv

### ▶️ Run locally:
```bash
git clone https://github.com/Abdinasir-Osman/SmartPhone_Backend.git
cd SmartPhone_Backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
