from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date, datetime
from services.historial import HistorialService
from database import Session
from models.listado_mensual import ListadoMensual as ListadoMensualModel
from services.servicios import ServiciosCliente as ServiciosClienteService
import json


def serializar_fechas(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()  # convierte a string "YYYY-MM-DD"
    raise TypeError(f"Tipo {type(obj)} no serializable")

def generar_listado_mensual():
    print(f"🕐 Generando listado mensual - {datetime.now()}")
    db = Session()  # tu sesión
    service = HistorialService(db)

    hoy = date.today()
    listado = service.listado_mensual(anio=hoy.year, mes=hoy.month, condicion_iva=None, 
        responsable_nombre=None)

    # Por defecto toma el mes actual
    #listado = service.listado_mensual()

    #listado = service.listar_por_filtros(None, None)
    if not listado:
        print("⚠️ No se generó ningún listado (vacío o error).")
        listado = []

    # Serializamos las fechas antes de guardar
    listado_serializado = json.loads(json.dumps(listado, default=serializar_fechas))

    # ✅ Asegura que contenido siempre sea una lista (aunque esté vacía)
    nuevo_listado = ListadoMensualModel(contenido=listado_serializado or [])

    db.query(ListadoMensualModel).delete()
    nuevo_listado = ListadoMensualModel(contenido=listado_serializado)
    db.add(nuevo_listado)
    db.commit()
    print(f"✅ Listado generado y guardado con {len(listado)} registros")
    db.close()


# def generar_listado_mensual():
#     print(f"🕐 Generando listado mensual - {datetime.now()}")
#     db = Session()
#     try:
#         service = HistorialService(db)
#         listado = service.listar_por_filtros(None, None)
#         print(f"✅ Listado generado con {len(listado)} registros")
#     except Exception as e:
#         print(f"❌ Error generando listado mensual: {e}")
#     finally:
#         db.close()

    #service = HistorialService(db)
    #listado = service.listar_por_filtros(None, None)
    #print(f"✅ Listado generado con {len(listado)} registros")
    #db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Ejecuta el 1 de cada mes a la medianoche
    #scheduler.add_job(generar_listado_mensual, "cron", day=1, hour=0, minute=0)
    scheduler.add_job(generar_listado_mensual, "interval", minutes=1) #para pruebas
    scheduler.start()
