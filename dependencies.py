from sqlalchemy.orm import sessionmaker
from models import db
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from config import SECRET_KEY, ALGORITHM
from models import User
from logger import logger
from main import oauth2_schema

SessionLocal = sessionmaker(bind=db.engine)

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def get_current_user(request: Request) -> User:
    if not hasattr(request.state, 'user'):
        logger.error("get_current_user chamado em rota não protegida pelo middleware")
        raise HTTPException(
            status_code=500, 
            detail="Erro interno: usuário não encontrado no contexto"
        )
    
    return request.state.user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.admin:
        logger.warning(f"Usuário sem privilégios admin tentando acessar: {current_user.email}")
        raise HTTPException(
            status_code=403, 
            detail="Acesso negado: privilégios de administrador requeridos"
        )
    
    logger.info(f"Admin {current_user.email} acessando recurso administrativo")
    return current_user

def require_admin_or_owner(
    resource_user_id: int,
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.admin or current_user.id == resource_user_id:
        return current_user
    
    logger.warning(f"Usuário {current_user.email} tentando acessar recurso de outro usuário")
    raise HTTPException(
        status_code=403,
        detail="Acesso negado: você só pode acessar seus próprios recursos"
    )

def verify_token(token: str = Depends(oauth2_schema), session: Session = Depends(get_session)):
    from jose import jwt, JWTError
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")