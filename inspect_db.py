from app.db import SessionLocal
from sqlalchemy import text
try:
    db = SessionLocal()
    res = db.execute(text("SELECT * FROM master_medical LIMIT 1")).mappings().first()
    if res:
        print("MasterMedical Columns:", list(res.keys()))
    else:
        print("MasterMedical: No rows")

    res_p = db.execute(text("SELECT * FROM pharmacy LIMIT 1")).mappings().first()
    if res_p:
        print("Pharmacy Columns:", list(res_p.keys()))
    else:
        print("Pharmacy: No rows")
except Exception as e:
    print("Error:", e)
