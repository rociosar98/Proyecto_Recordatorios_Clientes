from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
from database import get_database_session
from models.recordatorios import Recordatorios as RecordatoriosModel
from fastapi.encoders import jsonable_encoder
from middlewares.jwt_bearer import JWTBearer
from services.recordatorios import RecordatoriosService
from sqlalchemy.orm import Session, joinedload
from schemas.recordatorios import RecordatorioOut, PagoManualIn
from models.clientes import Clientes as ClientesModel
from models.servicios import Servicios as ServiciosModel, ServiciosCliente as ServiciosClienteModel
from datetime import date
from models.usuarios import Usuarios as UsuariosModel


recordatorios_router = APIRouter()


@recordatorios_router.post("/enviar-manual", tags=["Recordatorios"], status_code=200)
def enviar_recordatorios_manualmente(
    fecha: str = Query(..., description="Fecha simulada en formato YYYY-MM-DD"),
    db: Session = Depends(get_database_session)
):
    """
    Permite probar el envío de recordatorios como si fuera una fecha específica.
    Ejemplo: POST /recordatorios/enviar-manual?fecha=2025-11-10
    """
    try:
        fecha_simulada = date.fromisoformat(fecha)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usa YYYY-MM-DD.")
    
    # ---------- BORRAR RECORDATORIOS EXISTENTES PARA ESA FECHA ----------
    db.query(RecordatoriosModel).filter(
         RecordatoriosModel.fecha_recordatorio == fecha_simulada
     ).delete()
    db.commit()

    service = RecordatoriosService(db)

    #  # Evitar duplicados: solo generar recordatorios que aún no existen para esa fecha
    # existing = db.query(RecordatoriosModel).filter(
    #     RecordatoriosModel.fecha_recordatorio == fecha_simulada
    # ).all()

    # if not existing:
    #     # Generar recordatorios según el listado mensual
    #     nuevos = service.generar_recordatorios(fecha_simulada)
    # else:
    #     nuevos = []
    #     print(f"⚠️ Ya existen {len(existing)} recordatorios para {fecha_simulada}, no se generarán duplicados.")


    # Generar recordatorios según la fecha simulada
    nuevos = service.generar_recordatorios_desde_listado(fecha_simulada)

    # Enviar todos los pendientes (incluso los recién creados)
    resultado_envio = service.enviar_recordatorios()

    return {
        "fecha_simulada": fecha_simulada.isoformat(),
        "recordatorios_generados": len(nuevos),
        "recordatorios_enviados": len(resultado_envio),
        "detalles": resultado_envio
    }


# Ver recordatorios
@recordatorios_router.get("/recordatorios/generar", tags=['Recordatorios'], response_model=list, status_code=200)
def listar_recordatorios(db: Session = Depends(get_database_session)):
    service = RecordatoriosService(db)
    return service.listar_recordatorios()

