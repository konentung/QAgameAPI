import hashlib

class AuthManager:
    def __init__(self, db):
        self.db = db  # 改為儲存 db 實例

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password, is_admin=False):
        existing_user = self.db.find_user_by_username(username)
        if existing_user:
            return False, "Username already exists"

        hashed = self.hash_password(password)
        self.db.insert_user({
            "username": username,
            "password": hashed,
            "is_admin": is_admin
        })
        return True, "User registered successfully"

    def login_user(self, username, password):
        print(f"🔍 Attempting login for {username}")
        user = self.db.find_user_by_username(username)
        if not user:
            print(f"❌ User {username} not found")
            return False, "User not found", None

        hashed = self.hash_password(password)
        if user["password"] != hashed:
            print(f"❌ Incorrect password for {username}")
            return False, "Incorrect password", None

        is_admin = user.get("is_admin", False)
        print(f"✅ User {username} logged in successfully")
        return True, "Login successful", is_admin