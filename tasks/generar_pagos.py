from datetime import date
from database import Session
from models.pagos import Pagos, EstadoPago
from models.servicios import ServiciosCliente
from sqlalchemy import extract
from services.historial import toca_facturar
from tasks.calculo_pagos import calcular_monto_mes
from services.pagos import PagosService


def generar_pagos_mensuales():
    print("🧾 Generando pagos automáticos...")

    db = Session()
    try:
        hoy = date.today()
        anio = hoy.year
        mes = hoy.month
        primer_dia_mes = date(anio, mes, 1)

        servicios = (
            db.query(ServiciosCliente)
            .filter(ServiciosCliente.activo == True)
            .all()
        )

        generados = 0

        pagos_service = PagosService(db)

        for sc in servicios:

            # Verificar si toca facturar este servicio este mes
            if not toca_facturar(sc, anio, mes):
                continue

            # Verificar si YA existe un pago generado este mes
            pago_existente = (
                db.query(Pagos)
                .filter(
                    Pagos.servicio_cliente_id == sc.id,
                    extract('year', Pagos.fecha_facturacion) == anio,
                    extract('month', Pagos.fecha_facturacion) == mes
                )
                .first()
            )

            if pago_existente:
                continue  # no duplicar pagos

            # 3) Calcular monto real del mes
            valores = calcular_monto_mes(sc, anio, mes)
            monto_mes = valores["monto_mes"]

            if monto_mes <= 0:
                # Servicio ya pagado completamente o saldo a favor cubre todo
                continue

            # Registrar el pago usando PagosService para mantener total acumulado y envío de confirmación
            pagos_service.registrar_pago(
                servicio_cliente_id=sc.id,
                monto=monto_mes,
                fecha_facturacion=primer_dia_mes,
                fecha_pago=None,
                observaciones="Pago automático generado"
            )

            # Crear nuevo registro de pago
            # nuevo_pago = Pagos(
            #     servicio_cliente_id=sc.id,
            #     monto=monto_mes,
            #     #monto=sc.precio_congelado,
            #     fecha_facturacion=primer_dia_mes,
            #     fecha_pago = None,
            #     estado = EstadoPago.pendiente,
            #     observaciones = None
            # )

            #db.add(nuevo_pago)
            generados += 1
        print(f"✅ Pagos generados: {generados}")

        # db.commit()
        # print(f"✅ Pagos generados: {generados}")

    except Exception as e:
        db.rollback()
        print("❌ Error generando pagos:", e)

    finally:
        db.close()
