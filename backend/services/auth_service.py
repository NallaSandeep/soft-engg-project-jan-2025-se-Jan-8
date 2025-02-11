def register_user(data):
    return {"message": "User registered successfully", "userId": "generated_id"}

def login_user(data):
    if data.get("email") and data.get("password"):
        return {"token": "jwt_token_here", "role": "student", "userId": "generated_id"}
    return None

def logout_user(user_id):
    return bool(user_id)
