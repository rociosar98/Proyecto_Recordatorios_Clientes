from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from database import engine, Base
from middlewares.error_handler import ErrorHandler
from starlette.middleware.cors import CORSMiddleware
from routers.usuarios import usuarios_router
from routers.clientes import clientes_router
from routers.servicios import servicios_router
from routers.recordatorios import recordatorios_router
from routers.pagos import pagos_router
from routers.empresa import empresa_router
from routers.resumenes import resumen_router
from routers.historial import historial_router
#from routers.dashboard import dashboard_router
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.title = "Recordatorios para clientes"

app.add_middleware(ErrorHandler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios_router)
app.include_router(clientes_router)
app.include_router(servicios_router)
app.include_router(recordatorios_router)
app.include_router(pagos_router)
app.include_router(empresa_router)
app.include_router(resumen_router)
app.include_router(historial_router)

Base.metadata.create_all(bind=engine)

# 1. Servimos todos los archivos estáticos del directorio frontend en la ruta "/" (raíz)
# app.mount("/", StaticFiles(directory="frontend", html=True ), name="frontend")

#app.mount("/", StaticFiles(directory="html", html=True), name="frontend")
