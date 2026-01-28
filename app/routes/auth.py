"""
Authentication Routes
Login, Register, and Admin user management
"""

from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from app.services import email_service
from fastapi.security import OAuth2PasswordRequestForm
from bson import ObjectId
from datetime import datetime

from app.database import get_users_collection
from app.schemas.user import (
    UserCreate,
    UserLogin,
    SubAdminCreate,
    UserResponse,
    Token,
    UserListResponse
)
from app.models.user import UserDocument
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)
from app.middleware.rbac import get_admin_user

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks
):
    """
    Register a new user account.
    
    - Creates a new user with 'user' role
    - Returns JWT token on success
    """
    users_collection = get_users_collection()
    
    # Check if email already exists
    existing_user = await users_collection.find_one({"email": user_data.email.lower()})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user document
    hashed_password = hash_password(user_data.password)
    user_doc = UserDocument.create_document(
        email=user_data.email,
        hashed_password=hashed_password,
        name=user_data.name,
        role="user"
    )
    
    # Insert into database
    result = await users_collection.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    # Send welcome email
    background_tasks.add_task(
        email_service.send_welcome_email,
        user_data.email,
        user_data.name
    )
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": user_id,
            "email": user_data.email.lower(),
            "role": "user"
        }
    )
    
    # Prepare response
    user_response = UserResponse(
        id=user_id,
        email=user_data.email.lower(),
        name=user_data.name,
        role="user",
        is_active=True,
        created_at=user_doc["created_at"]
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and return JWT token.
    
    - Accepts email (as username) and password
    - Returns JWT token on success
    """
    users_collection = get_users_collection()
    
    # Find user by email
    user = await users_collection.find_one({"email": form_data.username.lower()})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify password
    if not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check if user is active
    if not user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Create access token
    user_id = str(user["_id"])
    access_token = create_access_token(
        data={
            "sub": user_id,
            "email": user["email"],
            "role": user["role"]
        }
    )
    
    # Prepare response
    user_response = UserResponse(
        id=user_id,
        email=user["email"],
        name=user["name"],
        role=user["role"],
        is_active=user["is_active"],
        created_at=user["created_at"]
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


@router.post("/admin/create-subadmin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_subadmin(
    subadmin_data: SubAdminCreate,
    current_user: dict = Depends(get_admin_user)
):
    """
    Create a new sub-admin account.
    
    - Admin only endpoint
    - Creates user with 'subadmin' role
    """
    users_collection = get_users_collection()
    
    # Check if email already exists
    existing_user = await users_collection.find_one({"email": subadmin_data.email.lower()})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create sub-admin document
    hashed_password = hash_password(subadmin_data.password)
    user_doc = UserDocument.create_document(
        email=subadmin_data.email,
        hashed_password=hashed_password,
        name=subadmin_data.name,
        role="subadmin"
    )
    
    # Insert into database
    result = await users_collection.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    return UserResponse(
        id=user_id,
        email=subadmin_data.email.lower(),
        name=subadmin_data.name,
        role="subadmin",
        is_active=True,
        created_at=user_doc["created_at"]
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user's profile.
    
    - Requires authentication
    - Returns user details excluding password
    """
    return UserResponse(
        id=current_user["_id"],
        email=current_user["email"],
        name=current_user["name"],
        role=current_user["role"],
        is_active=current_user["is_active"],
        created_at=current_user["created_at"]
    )


@router.get("/admin/users", response_model=UserListResponse)
async def list_users(
    page: int = 1,
    per_page: int = 20,
    role: str = None,
    current_user: dict = Depends(get_admin_user)
):
    """
    List all users.
    
    - Admin only endpoint
    - Supports pagination and role filtering
    """
    users_collection = get_users_collection()
    
    # Build query
    query = {}
    if role:
        query["role"] = role
    
    # Get total count
    total = await users_collection.count_documents(query)
    
    # Get paginated users
    skip = (page - 1) * per_page
    cursor = users_collection.find(query).skip(skip).limit(per_page)
    users = await cursor.to_list(length=per_page)
    
    # Format response
    user_responses = [
        UserResponse(
            id=str(user["_id"]),
            email=user["email"],
            name=user["name"],
            role=user["role"],
            is_active=user["is_active"],
            created_at=user["created_at"]
        )
        for user in users
    ]
    
    return UserListResponse(
        users=user_responses,
        total=total,
        page=page,
        per_page=per_page
    )


@router.delete("/admin/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: str,
    current_user: dict = Depends(get_admin_user)
):
    """
    Deactivate a user account.
    
    - Admin only endpoint
    - Soft delete (sets is_active to False)
    """
    users_collection = get_users_collection()
    
    # Check if user exists
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent self-deactivation
    if str(user["_id"]) == current_user["_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    # Deactivate user
    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    
    return None
