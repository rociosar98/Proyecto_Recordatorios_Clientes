from models.pagos import Pagos as PagoModel
from models.servicios import ServiciosCliente as ServiciosClienteModel
from sqlalchemy.orm import Session, joinedload
from datetime import date, datetime
from typing import List, Optional
from core.enums import EstadoPago
from sqlalchemy import func
from fastapi_mail import FastMail, MessageSchema, MessageType
from core.mail_config import fast_mail
from fastapi import BackgroundTasks


class PagosService:

    def __init__(self, db) -> None:
        self.db = db
        

    def registrar_pago(self, servicio_cliente_id: int, monto: float, fecha_facturacion: date,
    fecha_pago: Optional[date] = None, observaciones: Optional[str] = None, background_tasks: BackgroundTasks = None):
        # Verificar que el servicio exista
        servicio = self.db.query(ServiciosClienteModel).filter_by(id = servicio_cliente_id).first()
        if not servicio:
            raise Exception("Servicio del cliente no encontrado")
        
        # Obtener pagos previos
        pagos_previos = self.db.query(PagoModel).filter_by(servicio_cliente_id = servicio_cliente_id).all()
        total_pagado = sum(pago.monto for pago in pagos_previos) # incluye el nuevo pago
        #total_pagado = sum(p.monto for p in pagos_previos)

        # Sumar el nuevo pago
        total_pagado += monto

        # Obtener el monto total del servicio
        monto_total = servicio.precio_congelado

        # Determinar el estado del servicio
        if total_pagado >= monto_total:
            estado = EstadoPago.pagado
        elif total_pagado > 0:
            estado = EstadoPago.parcial
        else:
            estado = EstadoPago.pendiente

        nuevo_pago = PagoModel(
            servicio_cliente_id = servicio_cliente_id,
            monto = monto,
            fecha_facturacion = fecha_facturacion,
            fecha_pago = fecha_pago,
            estado = estado,
            observaciones = observaciones
        )

        self.db.add(nuevo_pago)
        self.db.commit()
        self.db.refresh(nuevo_pago)

        # Enviar confirmación automática
        self.enviar_confirmacion_pago(servicio, monto, fecha_pago or fecha_facturacion, background_tasks)

        return nuevo_pago
    
    def enviar_confirmacion_pago(self, servicio_cliente, monto: float, fecha, background_tasks: BackgroundTasks = None):
        cliente = servicio_cliente.cliente
        servicio = servicio_cliente.servicio

        mensaje = f"""
    ✅ *Confirmación de Pago Recibido*

    👤 Cliente: {cliente.nombre} {cliente.apellido}
    🏢 Empresa: {cliente.empresa}

    💰 Monto recibido: ${monto:.2f}
    🗓️ Fecha: {fecha.strftime('%d/%m/%Y')}
    🧾 Servicio: {servicio.nombre}

    ¡Gracias por tu pago!
    """
        
        # message = MessageSchema(
        #     subject="Confirmación de Pago",
        #     recipients=[cliente.correo],
        #     body=mensaje,
        #     subtype=MessageType.plain  # o html si querés usar HTML
        # )

        # if background_tasks:
        #     background_tasks.add_task(fast_mail.send_message, message)

        medio_contacto = cliente.metodo_aviso

        if medio_contacto in ["email", "ambos"] and background_tasks:
            self.enviar_email(destinatario=cliente.correo, asunto="Confirmación de Pago", cuerpo=mensaje, background_tasks=background_tasks)
        # if medio_contacto in ["whatsapp", "ambos"]:
        #     self.enviar_whatsapp(numero=cliente.whatsapp, mensaje=mensaje)

    def enviar_email(self, destinatario: str, asunto: str, cuerpo: str, background_tasks: BackgroundTasks):
        message = MessageSchema(
            subject=asunto,
            recipients=[destinatario],
            body=cuerpo,
            subtype=MessageType.html
        )
        if background_tasks:
            background_tasks.add_task(fast_mail.send_message, message)

    # def enviar_email(self, destinatario: str, asunto: str, cuerpo: str):
    #     print(f"[EMAIL] Enviando a {destinatario}:\nAsunto: {asunto}\n{cuerpo}")

    # def enviar_whatsapp(self, numero: str, mensaje: str):
    #     print(f"[WHATSAPP] Enviando a {numero}:\n{mensaje}")
    
    def listar_pagos(self) -> List[PagoModel]:
        return self.db.query(PagoModel).all()


    def obtener_resumen_pagos(self):
        # Traer todos los servicios asignados activos, con cliente, servicio y pagos
        servicios = (
            self.db.query(ServiciosClienteModel)
            .options(
                joinedload(ServiciosClienteModel.cliente),
                joinedload(ServiciosClienteModel.servicio),
                joinedload(ServiciosClienteModel.pagos)
            )
            .filter(ServiciosClienteModel.activo == True)
            .all()
        )

        resumenes = []
        for sc in servicios:
            cliente = sc.cliente
            servicio = sc.servicio

            monto_total = sc.precio_congelado
            pagos = sc.pagos or []
            total_pagado = sum(p.monto for p in pagos)

            # Calcular estado y saldo
            if total_pagado >= monto_total:
                estado = "pagado"
            elif total_pagado > 0:
                estado = "parcial"
            else:
                estado = "pendiente"

            #saldo = monto_total - total_pagado
            saldo = max(monto_total - total_pagado, 0)
            saldo_a_favor = max(total_pagado - monto_total, 0)

            resumenes.append({
                "servicio_cliente_id": sc.id,
                "cliente_nombre": f"{cliente.nombre} {cliente.apellido}",
                "empresa": cliente.empresa,
                "servicio": servicio.nombre,
                "monto_total": monto_total,
                "total_pagado": total_pagado,
                "estado": estado,
                "saldo": saldo,
                "saldo_a_favor": saldo_a_favor
            })

        return resumenes
    
   