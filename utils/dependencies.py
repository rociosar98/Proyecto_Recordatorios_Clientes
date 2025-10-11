from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from middlewares.jwt_bearer import JWTBearer
from database import get_database_session
from models.usuarios import Usuarios

def get_current_user(payload: dict = Depends(JWTBearer()), db: Session = Depends(get_database_session)):
    correo = payload.get("sub")
    if not correo:
        raise HTTPException(status_code=403, detail="Token sin datos de usuario")

    usuario = db.query(Usuarios).filter_by(correo=correo).first()
    if not usuario:
        raise HTTPException(status_code=403, detail="Usuario no encontrado")
    
    return usuario

def admin_required(usuario=Depends(get_current_user)):
    if usuario.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden acceder")