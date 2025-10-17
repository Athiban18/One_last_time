from app import app, db
from models import User

with app.app_context():
    users = User.query.all()
    print(f"Total users in database: {len(users)}")
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Type: {user.user_type}")
    
    if len(users) == 0:
        print("No users found in database. You may need to register first.") 