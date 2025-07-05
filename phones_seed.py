import pandas as pd
from sqlalchemy.orm import Session
from app.models.phone import Phone
from app.database import SessionLocal

# ✅ Load cleaned dataset
df = pd.read_csv(r"C:\Users\SCRPC\Desktop\ML\CBF\CBF_Cleaned.csv")

# ✅ Database session
db: Session = SessionLocal()

inserted = 0

try:
    for _, row in df.iterrows():
        model_name = row["Model"].strip()
        brand = row["Brand"].strip()
        phone_id = f"{brand}_{model_name}".replace(" ", "_")

        # ✅ Hubi haddii uu horey ugu jiro
        existing = db.query(Phone).filter(Phone.model_name == model_name).first()
        if not existing:
            new_phone = Phone(id=phone_id, model_name=model_name, brand=brand)
            db.add(new_phone)
            db.commit()
            inserted += 1

    print(f"✅ {inserted} new phones inserted successfully.")

except Exception as e:
    print("❌ Error seeding phones:", e)

finally:
    db.close()
