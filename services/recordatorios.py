from datetime import date
from sqlalchemy.orm import Session
from models.recordatorios import Recordatorios
from models.servicios import ServiciosCliente as ServiciosClienteModel
from schemas.recordatorios import RecordatorioOut
from models.pagos import Pagos as PagosModel


class RecordatoriosService():

    def __init__(self, db) -> None:
        self.db = db

    def generar_recordatorios_dia_1(self):
        hoy = date.today()
        # Para pruebas: descomentar la siguiente línea
        # hoy = date(2025, 11, 1)

        nuevos_recordatorios = []

        servicios_clientes = self.db.query(ServiciosClienteModel).filter(ServiciosClienteModel.activo == True).all()

        for sc in servicios_clientes:
            cliente = sc.cliente
            if not cliente:
                continue

            # Ignorar servicios fuera de rango de fechas
            if sc.fecha_inicio > hoy or (sc.fecha_vencimiento and sc.fecha_vencimiento < hoy):
                continue

            # Ignorar si el servicio no corresponde a este mes según recurrencia
            if not self.servicio_corresponde_a_mes(sc, hoy):
                continue

            # Calcular total pagado y saldo a favor
            pagos = self.db.query(PagosModel).filter_by(servicio_cliente_id=sc.id).all()
            total_pagado = sum(p.monto for p in pagos)
            monto_mes = sc.precio_congelado
            saldo_a_favor = max(total_pagado - monto_mes, 0)
            saldo_pendiente = max(monto_mes - total_pagado, 0)

            # Determinar estado
            if saldo_pendiente == 0:
                estado = "pagado"
                monto_a_mostrar = 0
            elif saldo_pendiente < monto_mes:
                estado = "parcial"
                monto_a_mostrar = saldo_pendiente
            else:
                estado = "pendiente"
                monto_a_mostrar = saldo_pendiente

            # Evitar duplicados de recordatorio
            ya_existe = self.db.query(Recordatorios).filter_by(
                servicio_cliente_id=sc.id,
                fecha_recordatorio=hoy,
                tipo_recordatorio="inicial"
            ).first()
            if ya_existe:
                continue

            # Calcular número de cuota si aplica
            numero_cuota = None
            if sc.cuotas:
                numero_cuota = (hoy.year - sc.fecha_inicio.year) * 12 + (hoy.month - sc.fecha_inicio.month) + 1
                if numero_cuota > sc.cuotas:
                    continue  # Ya completó el plan de cuotas

            nuevo = Recordatorios(
                servicio_cliente_id=sc.id,
                fecha_recordatorio=hoy,
                metodo_envio=cliente.metodo_aviso,
                tipo_recordatorio="inicial",
                numero_cuota=numero_cuota,
                enviado=False
            )
            self.db.add(nuevo)
            nuevos_recordatorios.append(nuevo)

        self.db.commit()
        return nuevos_recordatorios
    

    def servicio_corresponde_a_mes(self, sc: ServiciosClienteModel, hoy: date) -> bool:
        if sc.fecha_inicio > hoy:
            return False
        if sc.fecha_vencimiento and sc.fecha_vencimiento < hoy:
            return False

        meses_desde_inicio = (hoy.year - sc.fecha_inicio.year) * 12 + (hoy.month - sc.fecha_inicio.month)

        recurrencia = sc.tipo_recurrencia.lower() if sc.tipo_recurrencia else "pago único"

        if recurrencia == "mensual":
            return True
        elif recurrencia == "bimestral":
            return meses_desde_inicio % 2 == 0
        elif recurrencia == "trimestral":
            return meses_desde_inicio % 3 == 0
        elif recurrencia == "cuatrimestral":
            return meses_desde_inicio % 4 == 0
        elif recurrencia == "semestral":
            return meses_desde_inicio % 6 == 0
        elif recurrencia == "anual":
            return hoy.month == sc.fecha_inicio.month
        else:
            return True  # pago único

    

    # def servicio_esta_pagado(self, servicio_cliente_id: int) -> bool:
    #     pagos = self.db.query(PagosModel).filter_by(servicio_cliente_id=servicio_cliente_id).all()
    #     total_pagado = sum(p.monto for p in pagos)

    #     sc = self.db.query(ServiciosCliente).filter_by(id=servicio_cliente_id).first()
    #     if not sc:
    #         return False

    #     return total_pagado >= sc.precio_congelado


       
    
    
    def get_recordatorios(self):
        return self.db.query(Recordatorios).all()
    
    def marcar_como_enviado(self, id: int) -> bool:
        recordatorio = self.db.query(Recordatorios).filter_by(id=id).first()
        if not recordatorio:
            return False
        recordatorio.enviado = True
        self.db.commit()
        return True
    
    def delete_recordatorio(self, id: int) -> bool:
        recordatorio = self.db.query(Recordatorios).filter_by(id=id).first()
        if not recordatorio:
            return False
        self.db.delete(recordatorio)
        self.db.commit()
        return True


    def generar_recordatorios_dia_10(self):
        hoy = date.today()
        #hoy = date(2025, 10, 10)
        nuevos_recordatorios = []

        servicios_clientes = self.db.query(ServiciosClienteModel).filter(ServiciosClienteModel.activo == True).all()

        for sc in servicios_clientes:
            cliente = sc.cliente
            if not cliente:
                continue

            # Simulación de impago: si no hay recordatorio de tipo "inicial" marcado como enviado
            recordatorio_inicial = self.db.query(Recordatorios).filter_by(
                servicio_cliente_id = sc.id,
                tipo_recordatorio = "inicial",
                fecha_recordatorio = hoy.replace(day=1)  # del 1° del mes actual
            ).first()

            if not recordatorio_inicial:
                continue  # No se generó ni siquiera el inicial

            if not recordatorio_inicial.enviado:
                # Ya hubo intento de contacto, ahora toca recordatorio
                ya_existe = self.db.query(Recordatorios).filter_by(
                    servicio_cliente_id = sc.id,
                    tipo_recordatorio = "recordatorio",
                    fecha_recordatorio = hoy
                ).first()

                if not ya_existe:
                    nuevo = Recordatorios(
                        servicio_cliente_id = sc.id,
                        fecha_recordatorio = hoy,
                        metodo_envio = cliente.metodo_aviso,
                        tipo_recordatorio = "recordatorio",
                        enviado = False,
                        estado_pago = "pendiente"
                    )
                    self.db.add(nuevo)
                    nuevos_recordatorios.append(nuevo)

        self.db.commit()
        return nuevos_recordatorios
    
    def generar_recordatorios_dia_20(self):
        hoy = date.today()
        #hoy = date(2025, 11, 1)
        nuevos_recordatorios = []

        servicios_clientes = self.db.query(ServiciosClienteModel).filter(ServiciosClienteModel.activo == True).all()

        for sc in servicios_clientes:
            cliente = sc.cliente
            if not cliente:
                continue

            # Verificar si ya se generó el recordatorio de mora para este cliente en esta fecha
            ya_existe = self.db.query(Recordatorios).filter_by(
                servicio_cliente_id = sc.id,
                fecha_recordatorio = hoy,
                tipo_recordatorio = "mora"
            ).first()

            if ya_existe:
                continue

            # Verificar si tiene recordatorio "inicial" generado este mes pero no pagado (estado_pago no es "pagado")
            recordatorio_inicial = self.db.query(Recordatorios).filter(
                Recordatorios.servicio_cliente_id == sc.id,
                Recordatorios.tipo_recordatorio == "inicial",
                Recordatorios.fecha_recordatorio >= hoy.replace(day=1),
                Recordatorios.fecha_recordatorio <= hoy,
                Recordatorios.estado_pago != "pagado"
            ).first()

            if recordatorio_inicial:
                nuevo = Recordatorios(
                    servicio_cliente_id = sc.id,
                    fecha_recordatorio = hoy,
                    metodo_envio = cliente.metodo_aviso,
                    tipo_recordatorio = "mora",
                    enviado = False
                )
                self.db.add(nuevo)
                nuevos_recordatorios.append(nuevo)

        self.db.commit()
        return nuevos_recordatorios
    
    def generar_recordatorios_dia_28(self):
        hoy = date(2025, 10, 28)
        nuevos_recordatorios = []

        servicios_clientes = self.db.query(ServiciosClienteModel).filter(ServiciosClienteModel.activo == True).all()

        for sc in servicios_clientes:
            cliente = sc.cliente
            if not cliente:
                continue

            # Verificar si ya se generó un recordatorio de corte para este cliente en esta fecha
            ya_existe = self.db.query(Recordatorios).filter_by(
                servicio_cliente_id = sc.id,
                fecha_recordatorio = hoy,
                tipo_recordatorio = "corte"
            ).first()

            if ya_existe:
                continue

            # Verificar si tiene recordatorios no pagados este mes
            recordatorio_impago = self.db.query(Recordatorios).filter(
                Recordatorios.servicio_cliente_id == sc.id,
                Recordatorios.tipo_recordatorio.in_(["inicial", "recordatorio", "mora"]),
                Recordatorios.fecha_recordatorio >= hoy.replace(day=1),
                Recordatorios.fecha_recordatorio <= hoy,
                Recordatorios.estado_pago != "pagado"
            ).first()

            if recordatorio_impago:
                nuevo = Recordatorios(
                    servicio_cliente_id = sc.id,
                    fecha_recordatorio = hoy,
                    metodo_envio = cliente.metodo_aviso,
                    tipo_recordatorio = "corte",
                    enviado = False,
                    estado_pago = "pendiente"
                )
                self.db.add(nuevo)
                nuevos_recordatorios.append(nuevo)

        self.db.commit()
        return nuevos_recordatorios
    
    def enviar_recordatorios_no_enviados(self):
        pendientes = self.db.query(Recordatorios).filter_by(enviado=False).all()
        enviados = []

        print(f"[DEBUG] Total de recordatorios no enviados encontrados: {len(pendientes)}")

        for r in pendientes:
            try:
                cliente = r.servicio_cliente.cliente
                servicio = r.servicio_cliente.servicio

                if not cliente:
                    print(f"[ADVERTENCIA] Recordatorio ID {r.id} sin cliente asociado.")
                    continue

                mensaje = f"""
                📢 *Aviso de Pago Pendiente*

                👤 Cliente: {cliente.nombre} {cliente.apellido}
                🏢 Empresa: {cliente.empresa}
                🧾 Servicio: {servicio.nombre}
                📆 Fecha del recordatorio: {r.fecha_recordatorio.strftime('%d/%m/%Y')}
                ⚠️ Tipo de aviso: {r.tipo_recordatorio.upper()}
                """

                metodo = r.metodo_envio
                contacto_mail = cliente.correo
                contacto_whatsapp = cliente.telefono
                

                if metodo == "mail":
                    self.enviar_email(destinatario=contacto_mail, asunto="Aviso de Deuda", cuerpo=mensaje)
                    print(f"[EMAIL ENVIADO] A: {contacto_mail} | Cliente: {cliente.nombre} {cliente.apellido}")
                elif metodo == "whatsapp":
                    self.enviar_whatsapp(numero=contacto_whatsapp, mensaje=mensaje)
                    print(f"[WHATSAPP ENVIADO] A: {contacto_whatsapp} | Cliente: {cliente.nombre} {cliente.apellido}")
                elif metodo == "ambos":
                    self.enviar_email(destinatario=contacto_mail, asunto="Aviso de Deuda", cuerpo=mensaje)
                    print(f"[EMAIL ENVIADO] A: {contacto_mail} | Cliente: {cliente.nombre}{cliente.apellido}")
                    self.enviar_whatsapp(numero=contacto_whatsapp, mensaje=mensaje)
                    print(f"[WHATSAPP ENVIADO] A: {contacto_whatsapp} | Cliente: {cliente.nombre} {cliente.apellido}")
                else:
                    print(f"[ERROR] Método de aviso no soportado: {metodo}")
                    continue

                r.enviado = True
                enviados.append(r)

            except Exception as e:
                print(f"[ERROR] Falló el envío del recordatorio ID {r.id}: {e}")
                continue

        self.db.commit()
        print(f"[RESULTADO] Total enviados: {len(enviados)}")
        return {"enviados": [r.id for r in enviados]}

    
    def enviar_recordatorios(self):
        hoy = date.today()
        recordatorios = self.db.query(Recordatorios).filter(
            Recordatorios.enviado == False,
            Recordatorios.fecha_recordatorio == hoy
        ).all()

        enviados = []

        for r in recordatorios:
            cliente = r.servicio_cliente.cliente
            servicio = r.servicio_cliente.servicio

            mensaje = f"""
            📢 *Aviso de {r.tipo_recordatorio.upper()}*

            👤 Cliente: {cliente.nombre} {cliente.apellido}
            🏢 Empresa: {cliente.empresa}
            🧾 Servicio: {servicio.nombre}
            📅 Fecha: {r.fecha_recordatorio.strftime('%d/%m/%Y')}

            Por favor, regularice su situación si aún no lo ha hecho.
                    """

            contacto = cliente.correo if r.metodo_envio == "email" else cliente.telefono

            if r.metodo_envio == "email":
                self.enviar_email(contacto, f"Aviso de {r.tipo_recordatorio}", mensaje)
            else:
                self.enviar_whatsapp(contacto, mensaje)

            r.enviado = True
            enviados.append(r.id)

        self.db.commit()
        return {"enviados": enviados}
    
    def enviar_email(self, destinatario: str, asunto: str, cuerpo: str):
        print(f"[EMAIL] Enviando a {destinatario}:\nAsunto: {asunto}\n{cuerpo}")

    def enviar_whatsapp(self, numero: str, mensaje: str):
        print(f"[WHATSAPP] Enviando a {numero}:\n{mensaje}")



    
    # def registrar_pago_manual(self, servicio_cliente_id: int, tipo_pago: str):
    #     """
    #     tipo_pago: "parcial" o "pagado"
    #     """
    #     if tipo_pago not in ["parcial", "pagado"]:
    #         raise ValueError("Tipo de pago inválido")

    #     hoy = date.today()
    #     primer_dia_mes = hoy.replace(day=1)

    #     # 1. Registrar el pago en la tabla pagos
    #     nuevo_pago = PagosModel(
    #         servicio_cliente_id = servicio_cliente_id,
    #         monto = 0,  # Si no hay monto, podés poner 0 o pedirlo en el request
    #         fecha_pago = hoy,
    #         observaciones = f"Pago registrado manualmente como '{tipo_pago}'"
    #     )
    #     self.db.add(nuevo_pago)

    #     # 2. Actualizar estado de recordatorios del mes
    #     recordatorios = self.db.query(Recordatorios).filter(
    #         Recordatorios.servicio_cliente_id == servicio_cliente_id,
    #         Recordatorios.fecha_recordatorio >= primer_dia_mes,
    #         Recordatorios.fecha_recordatorio <= hoy,
    #         Recordatorios.tipo_recordatorio.in_(["inicial", "recordatorio", "mora", "corte"])
    #     ).all()

    #     if not recordatorios:
    #         return 0  # Nada para actualizar

    #     for r in recordatorios:
    #         r.estado_pago = tipo_pago

    #     self.db.commit()
    #     return len(recordatorios)
    
   