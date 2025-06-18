from fastapi import APIRouter, Depends, HTTPException
from models import User
from dependencies import get_session, get_current_user
from main import bcrypt_context
from config import ALGORITHM, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from schemas import UserSchema, LoginSchema
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

auth_router = APIRouter(prefix="/auth", tags=["auth"])


def create_token(user_id: int, duration: int = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiration = datetime.now(timezone.utc) + duration
    dict_info = {
        "sub": str(user_id),
        "exp": data_expiration,
    }
    
    enconded_jwt = jwt.encode(dict_info, key=SECRET_KEY, algorithm=ALGORITHM)

    return enconded_jwt

def auth_user(email:str, password:str, session: Session):
    user = session.query(User).filter(User.email == email).first()
    if not user:
        return None
    
    if not bcrypt_context.verify(password, user.password):
        return None
    
    return user

@auth_router.post("/register")
async def register(user_schema: UserSchema, session:Session = Depends(get_session)):
    user = session.query(User).filter(User.email == user_schema.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    else:
        encrypted_password = bcrypt_context.hash(user_schema.password)
        user = User(user_schema.name, user_schema.email, encrypted_password,user_schema.active, user_schema.admin)
        session.add(user)
        session.commit()
        return {"message": f"User registered successfully ID: {user.id}"}
    
@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(get_session)):
    user = auth_user(login_schema.email, login_schema.password, session)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_token(user.id)
    refresh_token = create_token(user.id, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@auth_router.get("/refresh")
async def refresh_token(current_user: User = Depends(get_current_user)):
    try:
        new_access_token = create_token(current_user.id)
        new_refresh_token = create_token(current_user.id, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
        return {"access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")