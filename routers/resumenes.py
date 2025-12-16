from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_database_session
from services.resumenes import ResumenesService

resumen_router = APIRouter(prefix="/resumenes", tags=["Resumenes"])

@resumen_router.post("/enviar", status_code=200)
def enviar_resumenes(background_tasks: BackgroundTasks, db: Session = Depends(get_database_session)):
    service = ResumenesService(db)
    enviados = service.enviar_resumenes(background_tasks)
    return {"resumenes_enviados": enviados}
