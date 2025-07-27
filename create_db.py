# create_db.py
from app import create_app, db
import os

app = create_app()

with app.app_context():
    # Print path for debugging
    from config import DATABASE_PATH
    print(f"📄 Creating database at: {DATABASE_PATH}")

    # Create all tables
    db.create_all()

    # Force file creation by touching it
    if not os.path.exists(DATABASE_PATH):
        open(DATABASE_PATH, 'w').close()
        print(f"✅ Created empty database file: {DATABASE_PATH}")
    else:
        print(f"ℹ️  Database file already exists: {DATABASE_PATH}")

    # Verify it exists
    print(f"✅ File exists: {os.path.isfile(DATABASE_PATH)}")