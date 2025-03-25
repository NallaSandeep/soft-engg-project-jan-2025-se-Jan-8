from app import create_app, db
from app.models import LectureProgress

def add_completed_at_column():
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text("ALTER TABLE lecture_progress ADD COLUMN completed_at DATETIME DEFAULT CURRENT_TIMESTAMP"))
            print("Successfully added completed_at column")
    except Exception as e:
        if "duplicate column name" not in str(e).lower():
            print(f"Error: {e}")
        else:
            print("Column already exists")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        add_completed_at_column() 