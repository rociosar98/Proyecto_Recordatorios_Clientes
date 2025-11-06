from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from database import get_database_session
from utils.dependencies import admin_required
from datetime import date

from models.pagos import Pagos

from models.datos_empresa import DatosEmpresa as DatosEmpresaModel
from schemas.datos_empresa import DatosEmpresa
#from services.empresa import EmpresaService
from services.dashboard import DashboardService

dashboard_router = APIRouter()


@dashboard_router.get("/empresa", tags=["Dashboard"], response_model=DatosEmpresa, status_code=status.HTTP_200_OK)
def obtener_datos_empresa(db: Session = Depends(get_database_session)):
    service = DashboardService(db)
    datos = service.get_datos_empresa()
    if not datos:
        raise HTTPException(status_code=404, detail="Datos de empresa no configurados")
    return datos

@dashboard_router.post("/empresa", tags=["Dashboard"], response_model=DatosEmpresa, status_code=status.HTTP_200_OK, dependencies=[Depends(admin_required)])
def crear_o_actualizar_datos_empresa(data: DatosEmpresa, db: Session = Depends(get_database_session)):
    service = DashboardService(db)
    datos = service.update_datos_empresa(data)
    return DatosEmpresa.from_orm(datos)
    #return datos



# Exportar pagos
@dashboard_router.get("/exportar", tags=["Dashboard"], dependencies=[Depends(admin_required)])
def exportar_datos(
    desde: date,
    hasta: date,
    formato: str = Query("csv", enum=["csv", "excel"]),
    db: Session = Depends(get_database_session),
):
    service = DashboardService(db)
    pagos = service.get_pagos_por_rango(desde, hasta)

    if not pagos:
        raise HTTPException(status_code=404, detail="No hay pagos en ese rango de fechas")

    buffer, filename = service.generar_archivo(pagos, desde, hasta, formato)

    media_type = "text/csv" if formato == "csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ext = ".csv" if formato == "csv" else ".xlsx"

    return StreamingResponse(
        buffer,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}{ext}"},
    )


# Limpiar pagos antiguos
@dashboard_router.delete("/exportar", tags=["Dashboard"], dependencies=[Depends(admin_required)])
def limpiar_datos(
    desde: date,
    hasta: date,
    confirmar: bool = Query(False),
    db: Session = Depends(get_database_session),
):
    service = DashboardService(db)
    total_pagos = service.get_pagos_por_rango(desde, hasta)
    total_count = len(total_pagos)

    if total_count == 0:
        raise HTTPException(status_code=404, detail="No hay pagos en ese rango de fechas")

    if not confirmar:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "mensaje": f"Se encontraron {total_count} pagos entre {desde} y {hasta}. "
                           f"Use 'confirmar=true' para proceder a la eliminación."
            },
        )

    eliminados = service.eliminar_pagos_por_rango(desde, hasta)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "mensaje": f"Eliminados {eliminados} pagos.",
            "rango": f"{desde} → {hasta}"
        },
    )

