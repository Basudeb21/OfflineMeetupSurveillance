from database import get_db
from sqlalchemy import text

def test_connection(db):
    """Test if DB connection works"""
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result and result[0] == 1:
            print("✅ Database connection successful!")
        else:
            print("❌ Database connected but test query failed.")
    except Exception as e:
        print("❌ Database connection failed:", e)

def show_sample_messages(db):
    """Fetch and print 5 latest messages from user_messages"""
    try:
        result = db.execute(
            text("SELECT * FROM user_messages ORDER BY id DESC LIMIT 5")
        ).mappings().all()  # .mappings() gives dict-like rows

        if result:
            print("✅ Sample messages from DB:")
            for row in result:
                print(row)
        else:
            print("No messages found in the table.")
    except Exception as e:
        print("Error fetching sample messages:", e)

if __name__ == "__main__":
    db_gen = get_db()
    db = next(db_gen)
    try:
        test_connection(db)
        show_sample_messages(db)
    finally:
        db.close()
