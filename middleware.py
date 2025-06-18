from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from sqlalchemy.orm import sessionmaker
from config import SECRET_KEY, ALGORITHM
from models import User, db
from logger import logger

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, public_paths: list = None):
        super().__init__(app)

        self.public_paths = public_paths or [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/auth/register",
            "/auth/login",
            "/auth/login-form"
        ]

        self.SessionLocal = sessionmaker(bind=db.engine)
    
    def is_public_path(self, path: str) -> bool:
        if path in self.public_paths:
            return True
        
        if path.startswith("/auth/"):
            return True
            
        return False
    
    def extract_token(self, request: Request) -> str:

        print(f"Headers recebidos: {dict(request.headers)}")
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            return authorization.split(" ")[1]
        
        token_cookie = request.cookies.get("csrftoken")
        if token_cookie:
            return token_cookie
            
        return None
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        if self.is_public_path(path):
            return await call_next(request)
        print("CHAMOU extract_token")
        token = self.extract_token(request)
        
        if not token:
            logger.warning(f"Tentativa de acesso sem token na rota: {path}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Token de acesso requerido"},
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            
            if not user_id:
                raise JWTError("Token sem identificação de usuário")
            
            session = self.SessionLocal()
            try:
                user = session.query(User).filter(User.id == int(user_id)).first()
                if not user:
                    logger.warning(f"Token válido mas usuário {user_id} não encontrado")
                    raise HTTPException(status_code=401, detail="Usuário não encontrado")
                
                request.state.user = user
                request.state.user_id = user.id
                
                logger.info(f"Usuário autenticado: {user.email} acessando {path}")
                
            finally:
                session.close()
                
        except JWTError as e:
            logger.warning(f"Token inválido na rota {path}: {str(e)}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Token inválido ou expirado"},
                headers={"WWW-Authenticate": "Bearer"}
            )
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        except Exception as e:
            logger.error(f"Erro interno no middleware de auth: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Erro interno do servidor"}
            )
        
        response = await call_next(request)
        return response


