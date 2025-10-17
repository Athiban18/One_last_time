from app import app, db
from models import User
from werkzeug.security import check_password_hash

def test_user_login(username, password):
    with app.app_context():
        user = User.query.filter(User.username.ilike(username)).first()
        if user:
            if check_password_hash(user.password, password):
                print(f"✅ Login successful for user: {username}")
                print(f"   User ID: {user.id}")
                print(f"   User Type: {user.user_type}")
                return True
            else:
                print(f"❌ Invalid password for user: {username}")
                return False
        else:
            print(f"❌ User not found: {username}")
            return False

# Test with existing user
print("Testing login functionality...")
test_user_login("xyz", "password")  # You'll need to know the actual password 