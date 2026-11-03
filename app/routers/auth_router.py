from fastapi import APIRouter, HTTPException, Depends, status, Response
from app.schemas.schemas import UserSignUp, UserSignIn, TokenResponse
from app.database import create_user, get_user_by_email, get_employee_profile
from app.auth import hash_password, verify_password, create_access_token, get_current_user
import uuid

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(data: UserSignUp):
    existing = get_user_by_email(data.email)
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email address already exists.")

    emp_id = data.employee_id or f"EMP-{uuid.uuid4().hex[:6].upper()}"
    hashed = hash_password(data.password)
    user_id = create_user(
        name=data.name,
        email=data.email,
        password_hash=hashed,
        employee_id=emp_id,
        department=data.department or "Engineering"
    )

    if not user_id:
        raise HTTPException(status_code=500, detail="Failed to create user account.")

    return {
        "success": True,
        "message": "Account created successfully! Please sign in with your credentials.",
        "user_id": user_id,
        "employee_id": emp_id
    }

@router.post("/signin", response_model=TokenResponse)
def signin(data: UserSignIn, response: Response):
    user = get_user_by_email(data.email)
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = create_access_token(data={"sub": str(user["id"]), "email": user["email"], "role": user["role"]})
    
    # Also set as http-only cookie for seamless browser navigation
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=False,
        max_age=86400,
        samesite="lax"
    )

    clean_user = {
        "id": user["id"],
        "employee_id": user["employee_id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "department": user["department"]
    }

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": clean_user
    }

@router.get("/me")
def get_current_profile(current_user: dict = Depends(get_current_user)):
    profile = get_employee_profile(current_user["id"])
    return {
        "user": {
            "id": current_user["id"],
            "employee_id": current_user["employee_id"],
            "name": current_user["name"],
            "email": current_user["email"],
            "role": current_user["role"],
            "department": current_user["department"]
        },
        "profile": profile
    }

@router.post("/signout")
def signout(response: Response):
    response.delete_cookie(key="access_token")
    return {"success": True, "message": "Signed out successfully."}

