from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_database_session
from services.resumenes import ResumenesService

resumen_router = APIRouter(prefix="/resumenes", tags=["Resumenes"])

@resumen_router.post("/enviar")
def enviar_resumenes(db: Session = Depends(get_database_session)):
    service = ResumenesService(db)
    enviados = service.enviar_resumenes()
    return {"resumenes_enviados": enviados}
