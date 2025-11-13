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
        """
    Genera recordatorios desde el listado mensual según la fecha simulada.
    - Día 10 → Recordatorio de deuda
    - Día 20 → Recordatorio de mora
    - Día 28 → Recordatorio de corte
    """
        
        # Determinar tipo de recordatorio según el día
        if fecha_simulada.day == 10:
            tipo_recordatorio = TipoRecordatorio.deuda
        elif fecha_simulada.day == 20:
            tipo_recordatorio = TipoRecordatorio.mora
        elif fecha_simulada.day == 28:
            tipo_recordatorio = TipoRecordatorio.corte
        else:
            print(f"⚠️ No se generan recordatorios: {fecha_simulada} no es un día 10, 20 o 28.")
            return []

        # Traer el último listado mensual
        listado = self.db.query(ListadoMensual).order_by(ListadoMensual.fecha.desc()).first()
        if not listado or not listado.contenido:
            print("⚠️ No se encontró un listado mensual para generar recordatorios.")
            return []
        
        recordatorios_generados = []


        # Agrupamos por cliente
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
            
        # Crear un recordatorio por cliente
        for cliente_id, datos in clientes_con_deuda.items():
            # Buscar un servicio_cliente asociado a ese cliente (cualquiera)
            # Buscar el servicio_cliente real
            sc = (
                self.db.query(ServiciosClienteModel)
                .filter(ServiciosClienteModel.cliente_id == cliente_id)
                .first()
            )
            if not sc: 
                #si no encuentra se salta
                continue

            #crear recordatorio
            recordatorio = RecordatoriosModel(
                servicio_cliente_id=sc.id,
                fecha_recordatorio=fecha_simulada,
                metodo_envio=sc.cliente.metodo_aviso,
                tipo_recordatorio=tipo_recordatorio,
                enviado=False,
                estado_pago=datos["estado"],
            )
            self.db.add(recordatorio)
            recordatorios_generados.append(recordatorio)

        self.db.commit()
        print(f"✅ Generados {len(recordatorios_generados)} recordatorios (uno por cliente).")
        return recordatorios_generados


            # Evitar duplicados
            # existe = self.db.query(RecordatoriosModel).filter(
            #     RecordatoriosModel.servicio_cliente_id == sc.id,
            #     RecordatoriosModel.fecha_recordatorio == fecha_simulada
            # ).first()
            # if existe:
            #     continue


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

            emoji = {
                "deuda": "📢",
                "mora": "⚠️",
                "corte": "🚨"
            }.get(rec.tipo_recordatorio.value, "📢")   

            msg = f"""
            {emoji} * Aviso de {rec.tipo_recordatorio.value.upper()} *

            👤 Cliente: {cliente.nombre} {cliente.apellido}
            🏢 Empresa: {cliente.empresa}

            🧾 Servicios:
            {servicios_texto}

            💰 Estado: {rec.estado_pago.value.capitalize()}
            📅 Fecha de vencimiento: {rec.fecha_recordatorio}

            Por favor, regularice su situación de pago. Muchas gracias.
            """ 
            
            # msg = (
            #     f"📢 * Aviso de DEUDA *\n\n"
            #     f"Cliente {cliente.nombre} {cliente.apellido}\n"
            #     f"Empresa: {cliente.empresa}\n\n"
            #     f"Servicios con saldo pendiente:\n{servicios_texto}\n\n"
            #     f"Fecha de vencimiento: {rec.fecha_recordatorio}\n\n"
            #     f"Por favor, regularice su situación de pago. Muchas gracias."
            # )

            if rec.metodo_envio in [MetodoAviso.mail, MetodoAviso.ambos]:
                print(f"[MAIL] Enviando a {cliente.correo}:\n{msg}\n{'-'*50}")

            if rec.metodo_envio in [MetodoAviso.whatsapp, MetodoAviso.ambos]:
                print(f"[WHATSAPP] Enviando a {cliente.whatsapp}:\n{msg}\n{'-'*50}")

            rec.enviado = True
            detalles_envio.append(f"{cliente.nombre} {cliente.apellido} - {rec.tipo_recordatorio.value}")

        self.db.commit()
        print(f"📨 Enviados {len(detalles_envio)} recordatorios (uno por cliente).")
        return detalles_envio


    # -----------------------------
    # Listar recordatorios
    # -----------------------------
    # def listar_recordatorios(self):
    #     return self.db.query(RecordatoriosModel).order_by(
    #         RecordatoriosModel.fecha_recordatorio.desc()
    #     ).all()

