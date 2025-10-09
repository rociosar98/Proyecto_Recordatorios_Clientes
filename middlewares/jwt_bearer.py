from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException
from utils.jwt_manager import create_token
from jose import jwt, JWTError

SECRET_KEY = "clave_secreta"
ALGORITHM = "HS256"


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if credentials.scheme != "Bearer":
                raise HTTPException(status_code=403, detail="Esquema de autenticación inválido")
        
            payload = self.verify_jwt(credentials.credentials)
            if payload is None:
                raise HTTPException(status_code=403, detail="Token inválido o expirado")
        
            return payload  # devuelve el diccionario con info del token (como "sub", "rol", etc.)
        else:
            raise HTTPException(status_code=403, detail="Credenciales no encontradas")

        
    def verify_jwt(self, token: str) -> dict | None:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError as e:
            print("❌ JWT Error:", e)
            return None
