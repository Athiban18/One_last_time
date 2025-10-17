from app import app, db

with app.app_context():
    # Create tables only if they don't exist (preserves user data)
    db.create_all()
    print("Database tables created/verified successfully!")
    print("Note: Existing user data is preserved.")


