from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date, datetime
from services.historial import HistorialService
from database import Session
from models.listado_mensual import ListadoMensual as ListadoMensualModel
from services.servicios import ServiciosCliente as ServiciosClienteService
from services.recordatorios import RecordatoriosService
import json
from tasks.generar_pagos import generar_pagos_mensuales


def serializar_fechas(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()  # convierte a string "YYYY-MM-DD"
    raise TypeError(f"Tipo {type(obj)} no serializable")


def generar_listado_mensual():
    print(f"🕐 Generando listado mensual - {datetime.now()}")
    db = Session()
    try:
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

        # Asegura que contenido siempre sea una lista (aunque esté vacía)
        nuevo_listado = ListadoMensualModel(contenido=listado_serializado or [])

        db.query(ListadoMensualModel).delete()
        db.add(nuevo_listado)
        db.commit()
        print(f"✅ Listado generado con {len(listado)} registros")
    except Exception as e:
        print(f"❌ Error generando listado mensual: {e}")
    finally:
        db.close()


# GENERACIÓN Y ENVÍO DE RECORDATORIOS (días 10, 20, 28)
def generar_y_enviar_recordatorios():
    hoy = date.today()
    print(f"📅 Verificando recordatorios automáticos - {hoy}")

    db = Session()
    try:
        service = RecordatoriosService(db)
        dia = hoy.day

        if dia not in [10, 20, 28]:
            print("ℹ️ Hoy no es día de recordatorios (solo 10, 20 o 28).")
            return

        # Generar recordatorios si no existen
        nuevos = service.generar_recordatorios(fecha=hoy)
        print(f"🧾 Recordatorios generados: {len(nuevos)}")

        # Enviar recordatorios pendientes
        enviados = service.enviar_recordatorios()
        print(f"✅ Recordatorios enviados: {len(enviados)}")
        for e in enviados:
            print(f"   - {e}")

    except Exception as e:
        print(f"❌ Error en recordatorios automáticos: {e}")
    finally:
        db.close()


def start_scheduler():
    scheduler = BackgroundScheduler()

    # Día 1 → genera listado mensual a las 00:00
    scheduler.add_job(generar_listado_mensual, "cron", day=1, hour=0, minute=0)
    #scheduler.add_job(generar_listado_mensual, "interval", minutes=1) # PARA PRUEBAS

    # Día 1 → generar pagos automáticos a las 00:05
    scheduler.add_job(generar_pagos_mensuales, "cron", day=1, hour=0, minute=5)

    # Todos los días a las 08:00 → revisa si corresponde enviar recordatorios (10, 20, 28)
    scheduler.add_job(generar_y_enviar_recordatorios, "cron", hour=8, minute=0)

    scheduler.start()
