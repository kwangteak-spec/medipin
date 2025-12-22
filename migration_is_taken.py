from app.db import engine
from sqlalchemy import text

def add_is_taken_column():
    with engine.connect() as conn:
        try:
            # Check if column exists first to avoid error
            result = conn.execute(text("SHOW COLUMNS FROM medication_schedule LIKE 'is_taken'"))
            if result.fetchone():
                print("Column 'is_taken' already exists.")
            else:
                conn.execute(text("ALTER TABLE medication_schedule ADD COLUMN is_taken BOOLEAN DEFAULT 0"))
                conn.commit()
                print("Successfully added is_taken column.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    add_is_taken_column()
