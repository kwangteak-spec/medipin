from app.db import engine
from sqlalchemy import text

with engine.connect() as conn:
    try:
        conn.execute(text('ALTER TABLE chat_history ADD COLUMN conversation_id VARCHAR(50)'))
        conn.commit()
        print("Successfully added conversation_id column.")
    except Exception as e:
        print(f"Error or already exists: {e}")
