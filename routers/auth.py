from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from backend.schemas.schemas import AdminLogin, Token, PasswordUpdate
from backend.database import admin_collection
from backend.utils.security import verify_password, hash_password, create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

async def get_current_admin(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    admin = await admin_collection.find_one({"username": username})
    if admin is None:
        raise credentials_exception
    return admin

@router.post("/login", response_model=Token)
async def login(form_data: AdminLogin):
    # Try finding the admin by username
    admin = await admin_collection.find_one({"username": form_data.username})
    if not admin or not verify_password(form_data.password, admin["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": admin["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def read_users_me(current_admin: dict = Depends(get_current_admin)):
    return {"username": current_admin["username"]}

@router.put("/password", status_code=status.HTTP_200_OK)
async def update_password(data: PasswordUpdate, current_admin: dict = Depends(get_current_admin)):
    # Verify old password
    if not verify_password(data.old_password, current_admin["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    
    # Hash and update
    hashed_pwd = hash_password(data.new_password)
    await admin_collection.update_one(
        {"username": current_admin["username"]},
        {"$set": {"password": hashed_pwd}}
    )
    return {"message": "Password updated successfully"}
