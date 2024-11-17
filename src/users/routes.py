# External imports
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Tuple

# Internal imports
from users.models import User, UserCreate, UserCreateResponse
from database import fetch_query, execute_query
from users.dependencies import check_token
from users.utils import get_password_hash, check_password

users_router = APIRouter()

# Sign up and create a new account
@users_router.post("/users", tags=["users"], response_model=UserCreateResponse)
async def new_user(user: UserCreate):
    # Check if username already exists
    existing_user = fetch_query("SELECT * FROM users WHERE username = %s", (user.username,))
    if existing_user:
        raise HTTPException(status_code=409, detail="Username already registered")

    # Check if email already exists
    existing_email = fetch_query("SELECT * FROM users WHERE email = %s", (user.email,))
    if existing_email:
        raise HTTPException(status_code=409, detail="Email already registered")

    if not check_password(user.password):
        raise HTTPException(status_code=400, detail="Password does not meet the required criteria. Must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character.")

    # Hash password
    hashed_password = get_password_hash(user.password)
    
    # Insert new user into the database
    execute_query("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (user.username, user.email, hashed_password))

    return {"message": "New account created successfully", "username": user.username}

# Get all users
@users_router.get("/users", tags=["users"], response_model=List[User])
async def get_all_users():
    # Fetch all users from the database
    all_users = fetch_query("SELECT id, username, email, joined_at FROM users")
    
    # If no users found, return an empty list
    if not all_users:
        return []
    
    # Convert each dictionary (row) into a User model instance
    users_list = []

    for user in all_users:
        users_list.append({"user_id": user["id"], "username": user["username"], "email": user["email"], "joined_at": user["joined_at"]})
    
    return users_list

# Protected route (requires authentication) !!! Must be before '/users/{user_id}' endpoint !!!
@users_router.get("/users/me", tags=["users"], response_model=User)
async def get_authorized_user(current_user: Tuple[int, str] = Depends(check_token)):
    user = fetch_query("SELECT * FROM users WHERE id = %s", (current_user[0],))[0]
    return {"user_id": user["id"], "username": user["username"], "email": user["email"], "joined_at": user["joined_at"]}

# Get a user by ID
@users_router.get("/users/{user_id}", tags=["users"], response_model=User)
async def get_user(user_id: int):
    user = fetch_query("SELECT * FROM users WHERE id = %s", (user_id,))[0]
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user["id"], "username": user["username"], "email": user["email"], "joined_at": user["joined_at"]}