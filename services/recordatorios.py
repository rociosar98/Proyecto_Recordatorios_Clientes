from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from models.recordatorios import Recordatorios as RecordatoriosModel
from models.servicios import ServiciosCliente as ServiciosClienteModel
from schemas.recordatorios import RecordatorioOut
from models.pagos import Pagos as PagosModel
from core.enums import TipoRecordatorio, MetodoAviso, EstadoPago
from models.clientes import Clientes as ClientesModel
from models.servicios import Servicios as ServiciosModel
from models.listado_mensual import ListadoMensual

class RecordatoriosService:
    def __init__(self, db: Session) -> None:
         self.db = db

    
    def generar_recordatorios_desde_listado(self, fecha_simulada: date):
    # Traer el último listado mensual
        listado = self.db.query(ListadoMensual).order_by(ListadoMensual.fecha.desc()).first()
        if not listado or not listado.contenido:
            return []
        
        recordatorios_generados = []


        # 🔹 Agrupamos por cliente
        clientes_con_deuda = {}

        for item in listado.contenido:
            estado = item["estado"]
            if estado not in ["pendiente", "parcial"]:
                continue

            cliente_id = item["cliente"]["id"]
            cliente_nombre = f"{item['cliente']['nombre']} {item['cliente']['apellido']}"

            if cliente_id not in clientes_con_deuda:
                clientes_con_deuda[cliente_id] = {
                    "cliente": item["cliente"],
                    "servicios": [],
                    "estado": estado,
                }

            clientes_con_deuda[cliente_id]["servicios"].append(
            {
                "nombre": item["servicio"]["nombre"],
                "monto": item["monto"],
            }
        )
            
        # 🔹 Crear un recordatorio por cliente
        for cliente_id, datos in clientes_con_deuda.items():
            # Buscar un servicio_cliente asociado a ese cliente (cualquiera)
            sc = (
                self.db.query(ServiciosClienteModel)
                .filter(ServiciosClienteModel.cliente_id == cliente_id)
                .first()
            )
            if not sc:
                continue

            recordatorio = RecordatoriosModel(
                servicio_cliente_id=sc.id,
                fecha_recordatorio=fecha_simulada,
                metodo_envio=sc.cliente.metodo_aviso,
                tipo_recordatorio=TipoRecordatorio.deuda,
                enviado=False,
                estado_pago=datos["estado"],
            )
            self.db.add(recordatorio)
            recordatorios_generados.append(recordatorio)

        self.db.commit()
        print(f"✅ Generados {len(recordatorios_generados)} recordatorios (uno por cliente).")
        return recordatorios_generados

            


        # for item in listado.contenido:
        #     # Buscar el servicio_cliente real
        #     sc = (
        #         self.db.query(ServiciosClienteModel)
        #         .join(ClientesModel)
        #         .join(ServiciosModel)
        #         .filter(
        #             ClientesModel.id == item["cliente"]["id"],
        #             ServiciosModel.id == item["servicio"]["id"]
        #         )
        #         .first()
        #     )
        #     if not sc:
        #         # Si no se encuentra, se salta
        #         continue

            # Evitar duplicados
            # existe = self.db.query(RecordatoriosModel).filter(
            #     RecordatoriosModel.servicio_cliente_id == sc.id,
            #     RecordatoriosModel.fecha_recordatorio == fecha_simulada
            # ).first()
            # if existe:
            #     continue

            # Crear recordatorio
        #     recordatorio = RecordatoriosModel(
        #         servicio_cliente_id=sc.id,
        #         fecha_recordatorio=fecha_simulada,
        #         metodo_envio=MetodoAviso.ambos,  # o según la lógica
        #         tipo_recordatorio=TipoRecordatorio.deuda,
        #         enviado=False,
        #         estado_pago=item["estado"],  # pendiente/parcial/pagado
        #         numero_cuota=item.get("servicio", {}).get("cuotas")
        #     )
        #     self.db.add(recordatorio)
        #     recordatorios_generados.append(recordatorio)

        # self.db.commit()
        # return recordatorios_generados


    
    # def listado_mensual(self, anio: int, mes: int):
    #     """
    #     Retorna el listado mensual ya calculado, usando la función existente
    #     que hace todos los cálculos de pagos y estados.
    #     """
    #     # Suponiendo que este método llama al service que ya definiste
    #     from services.historial import HistorialService
    #     historial_service = HistorialService(self.db)
    #     return historial_service.listado_mensual(anio, mes)

    # def generar_recordatorios(self, fecha_simulada: date):
    #     """
    #     Genera recordatorios a partir del listado mensual.
    #     Solo genera para estado pendiente o parcial.
    #     """
    #     anio = fecha_simulada.year
    #     mes = fecha_simulada.month

    #     listado = self.listado_mensual(anio, mes)
    #     recordatorios_generados = []

    #     for item in listado:
    #         if item['estado'] not in ['pendiente', 'parcial']:
    #             continue

    #         cliente_id = item['cliente']['id']
    #         servicio_id = item['servicio']['id']
    #         monto = item['monto']
    #         estado = EstadoPago(item['estado'])

    #         # Crear recordatorios de distintos tipos
    #         for tipo, dia in [(TipoRecordatorio.deuda, 10),
    #                           (TipoRecordatorio.mora, 20),
    #                           (TipoRecordatorio.corte, 28)]:
    #             # Ajuste: evitar fechas inválidas en meses cortos
    #             dia_recordatorio = min(dia, 28)
    #             fecha_recordatorio = date(anio, mes, dia_recordatorio)

    #             recordatorio = RecordatoriosModel(
    #                 servicio_cliente_id=servicio_id,
    #                 fecha_recordatorio=fecha_recordatorio,
    #                 metodo_envio=MetodoAviso.ambos,
    #                 tipo_recordatorio=tipo,
    #                 enviado=False,
    #                 estado_pago=estado,
    #                 numero_cuota=item['servicio'].get('cuotas')
    #             )
    #             self.db.add(recordatorio)
    #             recordatorios_generados.append(recordatorio)

    #     self.db.commit()
    #     print(f"✅ Generados {len(recordatorios_generados)} recordatorios.")
    #     return recordatorios_generados

    def enviar_recordatorios(self):
        """
        Envía todos los recordatorios pendientes.
        Retorna un dict con detalles de envío.
        """
        pendientes = self.db.query(RecordatoriosModel).filter(RecordatoriosModel.enviado == False).all()

        detalles_envio = []

        for rec in pendientes:
            cliente = rec.servicio_cliente.cliente

            # Obtener servicios con deuda de ese cliente
            listado = (
                self.db.query(ListadoMensual)
                .order_by(ListadoMensual.fecha.desc())
                .first()
            )
            servicios_cliente = [
                i for i in listado.contenido
                if i["cliente"]["id"] == cliente.id and i["estado"] in ("pendiente", "parcial")
            ]

            servicios_texto = "\n".join(
                [f"• {s['servicio']['nombre']}: ${s['monto']}" for s in servicios_cliente]
            )

            msg = (
                f"📢 * Aviso de DEUDA *\n\n"
                f"Cliente {cliente.nombre} {cliente.apellido}\n"
                f"Empresa: {cliente.empresa}\n\n"
                f"Servicios con saldo pendiente:\n{servicios_texto}\n\n"
                f"Fecha de vencimiento: {rec.fecha_recordatorio}\n\n"
                f"Por favor, regularice su situación de pago. Muchas gracias."
            )

            if rec.metodo_envio in [MetodoAviso.mail, MetodoAviso.ambos]:
                print(f"[MAIL] Enviando a {cliente.correo}:\n{msg}\n{'-'*50}")

            if rec.metodo_envio in [MetodoAviso.whatsapp, MetodoAviso.ambos]:
                print(f"[WHATSAPP] Enviando a {cliente.whatsapp}:\n{msg}\n{'-'*50}")

            rec.enviado = True
            detalles_envio.append(f"{cliente.nombre} {cliente.apellido} - deuda")

        self.db.commit()
        print(f"📨 Enviados {len(detalles_envio)} recordatorios (uno por cliente).")
        return detalles_envio

        # for rec in pendientes:
        #     # Simulación de envío según método
        #     msg = (
        #         f"📢 *Aviso de {rec.tipo_recordatorio.value.upper()}*\n\n"
        #         f"Hola {rec.servicio_cliente.cliente.nombre} {rec.servicio_cliente.cliente.apellido},\n"
        #         f"Empresa: {rec.servicio_cliente.cliente.empresa}\n"
        #         f"Servicio: {rec.servicio_cliente.servicio.nombre}\n\n"
        #         f"Monto a pagar: ${rec.servicio_cliente.precio_congelado:.2f}\n"
        #         f"Fecha de vencimiento: {rec.fecha_recordatorio}\n\n"
        #         f"Por favor, regularice su situación de pago. Muchas gracias."
        #     )

        #     if rec.metodo_envio in [MetodoAviso.mail, MetodoAviso.ambos]:
        #         print(f"[MAIL] Enviando a {rec.servicio_cliente.cliente.correo}:\n{msg}\n{'-'*50}")

        #     if rec.metodo_envio in [MetodoAviso.whatsapp, MetodoAviso.ambos]:
        #         print(f"[WHATSAPP] Enviando a {rec.servicio_cliente.cliente.whatsapp}:\n{msg}\n{'-'*50}")

        #     rec.enviado = True
        #     detalles_envio.append(f"{rec.servicio_cliente.cliente.nombre} {rec.servicio_cliente.cliente.apellido} - {rec.tipo_recordatorio.value}")

        # self.db.commit()
        # print(f"📨 Enviados {len(detalles_envio)} recordatorios.")
        # return detalles_envio







    # -----------------------------
    # Generar recordatorios según estado de pagos
    # -----------------------------
    # def generar_recordatorios(self, fecha: date = None):
    #     """
    #     Genera recordatorios para todos los servicios con pagos pendientes.
    #     Se pueden crear 3 tipos:
    #     - Recordatorio normal o deuda (día 10)
    #     - Alerta de mora (día 20)
    #     - Alerta de corte (día 28)
    #     """
    #     fecha = fecha or date.today()
    #     recordatorios_generados = []

    #     servicios = self.db.query(ServiciosClienteModel).filter(
    #         ServiciosClienteModel.activo == True
    #     ).all()

    #     for sc in servicios:
    #         # Determinar estado del pago (pendiente, parcial, pagado)
    #         estado = self._calcular_estado_pago(sc, fecha)

    #         # Solo recordatorios para servicios con deuda
    #         if estado in [EstadoPago.pendiente, EstadoPago.parcial]:
    #             for tipo, dia in [
    #                 (TipoRecordatorio.deuda, 10),
    #                 (TipoRecordatorio.mora, 20),
    #                 (TipoRecordatorio.corte, 28)
    #             ]:
    #                 fecha_record = date(fecha.year, fecha.month, dia)

    #                 # ver si ya existe
    #                 existe = (
    #                     self.db.query(RecordatorioModel)
    #                     .filter_by(
    #                         servicio_cliente_id=sc.id,
    #                         tipo_recordatorio=tipo,
    #                         fecha_recordatorio=fecha_record,
    #                     )
    #                     .first()
    #                 )
    #                 if existe:
    #                     continue

    #                 # Crear según método de aviso del cliente
    #                 metodo_cliente = sc.cliente.metodo_aviso or MetodoAviso.ambos

    #                 if metodo_cliente == MetodoAviso.ambos:
    #                     metodos = [MetodoAviso.mail, MetodoAviso.whatsapp]
    #                 else:
    #                     metodos = [metodo_cliente]

    #                 for metodo in metodos:
    #                     record = RecordatorioModel(
    #                         servicio_cliente_id=sc.id,
    #                         fecha_recordatorio=fecha_record,
    #                         tipo_recordatorio=tipo,
    #                         metodo_envio=metodo,
    #                         enviado=False,
    #                         estado_pago=estado,
    #                     )
    #                     self.db.add(record)
    #                     recordatorios_generados.append(record)

    #     self.db.commit()
    #     print(f"✅ Generados {len(recordatorios_generados)} recordatorios.")
    #     return recordatorios_generados


    # # -----------------------------
    # # Enviar recordatorios pendientes
    # # -----------------------------
    # def enviar_recordatorios(self, fecha: date = None):
    #     """
    #     Envía todos los recordatorios pendientes cuya fecha sea <= hoy.
    #     """
    #     #hoy = date.today()
    #     fecha = fecha or date.today()
    #     pendientes = (
    #         self.db.query(RecordatorioModel)
    #         .join(ServiciosClienteModel)
    #         .filter(
    #             RecordatorioModel.enviado == False,
    #             RecordatorioModel.fecha_recordatorio <= fecha,
    #         )
    #         .all()
    #     )

    #     enviados = []

    #     for r in pendientes:
    #         sc = r.servicio_cliente
    #         cliente = sc.cliente
    #         mensaje = self._generar_mensaje(r, sc, cliente)

    #         if r.metodo_envio == MetodoAviso.mail:
    #             self._enviar_mail(cliente.correo, mensaje)
    #         elif r.metodo_envio == MetodoAviso.whatsapp:
    #             self._enviar_whatsapp(cliente.whatsapp, mensaje)
    #         elif r.metodo_envio == MetodoAviso.ambos:
    #             self._enviar_mail(cliente.correo, mensaje)
    #             self._enviar_whatsapp(cliente.whatsapp, mensaje)

    #         r.enviado = True
    #         self.db.add(r)
    #         enviados.append(f"{cliente.nombre} {cliente.apellido} - {r.tipo_recordatorio.value}")

    #     self.db.commit()
    #     print(f"📨 Enviados {len(enviados)} recordatorios.")
    #     return enviados

    # -----------------------------
    # Listar recordatorios
    # -----------------------------
    # def listar_recordatorios(self):
    #     return self.db.query(RecordatoriosModel).order_by(
    #         RecordatoriosModel.fecha_recordatorio.desc()
    #     ).all()

    # -----------------------------
    # Helpers internos
    # -----------------------------
    # def _calcular_estado_pago(self, sc, fecha):
    #     """Determina el estado del pago del servicio"""
    #     pagos = sc.pagos or []
    #     total_pagado = sum(p.monto for p in pagos if p.fecha_facturacion and p.fecha_facturacion <= fecha)
    #     monto_mes = sc.precio_congelado
    #     if total_pagado >= monto_mes:
    #         return EstadoPago.pagado
    #     elif total_pagado > 0:
    #         return EstadoPago.parcial
    #     else:
    #         return EstadoPago.pendiente

#     def _generar_mensaje(self, recordatorio, sc, cliente):
#         tipo = recordatorio.tipo_recordatorio.value
#         monto = sc.precio_congelado
#         return f"""

# 📢 *Aviso de {tipo.upper()}*
        
# Hola {cliente.nombre} {cliente.apellido},
# Empresa: {cliente.empresa}
# Servicio: {sc.servicio.nombre}

# Monto a pagar: ${monto:.2f}
# Fecha de vencimiento: {recordatorio.fecha_recordatorio}

# Por favor, regularice su situación de pago. Muchas gracias.
# Gracias.
#         """.strip()
    

# Cliente: {cliente.nombre} {cliente.apellido}
# 📅 Fecha del aviso: {recordatorio.fecha_recordatorio.strftime('%d/%m/%Y')}
#         """.strip()

    # -----------------------------
    # Métodos simulados de envío
    # -----------------------------
    # def _enviar_mail(self, correo, mensaje):
    #     if correo:
    #         print(f"[MAIL] Enviando a {correo}:\n{mensaje}\n{'-'*50}")

    # def _enviar_whatsapp(self, numero, mensaje):
    #     if numero:
    #         print(f"[WHATSAPP] Enviando a {numero}:\n{mensaje}\n{'-'*50}")





# class RecordatoriosService:

#     def __init__(self, db: Session) -> None:
#         self.db = db

#     # ---------- MÉTODOS AUXILIARES ----------

#     def saldo_pendiente_mes(self, sc: ServiciosClienteModel, hoy: date) -> float:
#         """Calcula el saldo pendiente del mes actual para un servicio cliente"""
#         pagos_mes = self.db.query(PagosModel).filter(
#             PagosModel.servicio_cliente_id == sc.id,
#             PagosModel.fecha_pago >= hoy.replace(day=1),
#             PagosModel.fecha_pago <= hoy
#         ).all()
#         total_pagado = sum(p.monto for p in pagos_mes)
#         return max(sc.precio_congelado - total_pagado, 0)

#     def ya_existe_recordatorio(self, sc: ServiciosClienteModel, tipo: str, fecha: date) -> bool:
#         """Verifica si ya existe un recordatorio de este tipo y fecha para el cliente"""
#         return self.db.query(Recordatorios).filter_by(
#             servicio_cliente_id = sc.id,
#             fecha_recordatorio = fecha,
#             tipo_recordatorio = tipo
#         ).first() is not None

#     def crear_recordatorio(self, sc: ServiciosClienteModel, tipo: str, hoy: date) -> Recordatorios:
#         """Crea y agrega un nuevo recordatorio a la sesión de DB"""
#         r = Recordatorios(
#             servicio_cliente_id = sc.id,
#             fecha_recordatorio = hoy,
#             metodo_envio = sc.cliente.metodo_aviso,
#             tipo_recordatorio = tipo,
#             enviado = False
#         )
#         self.db.add(r)
#         return r

#     # ---------- GENERAR RECORDATORIOS ----------

#     def generar_recordatorios(self, tipo: str):
#         """Genera recordatorios según tipo: 'deuda', 'mora' o 'corte'"""
#         hoy = date.today()
#         nuevos_recordatorios = []

#         servicios_clientes = self.db.query(ServiciosClienteModel).filter(ServiciosClienteModel.activo == True).all()

#         for sc in servicios_clientes:
#             cliente = sc.cliente
#             if not cliente:
#                 continue

#             saldo = self.saldo_pendiente_mes(sc, hoy)
#             if saldo <= 0:
#                 continue  # No hay deuda

#             if self.ya_existe_recordatorio(sc, tipo, hoy):
#                 continue

#             nuevo = self.crear_recordatorio(sc, tipo, hoy)
#             nuevos_recordatorios.append(nuevo)

#         self.db.commit()
#         return nuevos_recordatorios

#     # ---------- ENVÍO DE RECORDATORIOS ----------

#     def enviar_recordatorios(self):
#         pendientes = self.db.query(Recordatorios).filter_by(enviado=False).all()
#         enviados = []

#         for r in pendientes:
#             cliente = r.servicio_cliente.cliente
#             servicio = r.servicio_cliente.servicio

#             mensaje = f"""
#             📢 Aviso: {r.tipo_recordatorio.value.upper()}
#             Cliente: {cliente.nombre} {cliente.apellido}
#             Empresa: {cliente.empresa}
#             Servicio: {servicio.nombre}
#             Fecha: {r.fecha_recordatorio.strftime('%d/%m/%Y')}
#             """

#             metodo = r.metodo_envio
#             if metodo == "mail":
#                 self.enviar_email(cliente.correo, f"Aviso de {r.tipo_recordatorio.value}", mensaje)
#             elif metodo == "whatsapp":
#                 self.enviar_whatsapp(cliente.telefono, mensaje)
#             elif metodo == "ambos":
#                 self.enviar_email(cliente.correo, f"Aviso de {r.tipo_recordatorio.value}", mensaje)
#                 self.enviar_whatsapp(cliente.telefono, mensaje)

#             r.enviado = True
#             enviados.append(r.id)

#         self.db.commit()
#         return {"enviados": enviados}

#     # ---------- MÉTODOS DE ENVÍO SIMULADOS ----------

#     def enviar_email(self, destinatario: str, asunto: str, cuerpo: str):
#         print(f"[EMAIL] Enviando a {destinatario} - {asunto}\n{cuerpo}")

#     def enviar_whatsapp(self, numero: str, mensaje: str):
#         print(f"[WHATSAPP] Enviando a {numero}\n{mensaje}")
