from sqlalchemy.orm import Session, joinedload
from models.clientes import Clientes as ClientesModel
from models.servicios import ServiciosCliente as ServiciosClienteModel
from models.servicios import Servicios as ServicioModel
from models.pagos import Pagos as PagoModel
from models.datos_empresa import DatosEmpresa as DatosEmpresaModel
from models.listado_mensual import ListadoMensual as ListadoMensualModel
from datetime import date
from fastapi_mail import FastMail, MessageSchema, MessageType
from core.mail_config import conf, fast_mail
from fastapi import BackgroundTasks


class ResumenesService:

    def __init__(self, db) -> None:
        self.db = db
        

    def enviar_resumenes(self, background_tasks: BackgroundTasks):
        # Obtener el último listado mensual
        listado = (
            self.db.query(ListadoMensualModel)
            .order_by(ListadoMensualModel.fecha.desc())
            .first()
        )

        if not listado or not listado.contenido:
            print("⚠️ No hay listado mensual generado para enviar.")
            return []

        # Datos de la empresa (CBU, CVU, etc.)
        datos_empresa = self.db.query(DatosEmpresaModel).first()
        if not datos_empresa:
            print("⚠️ No hay datos de empresa configurados.")
            return []

        # Agrupar servicios por cliente
        clientes_dict = {}
        for item in listado.contenido:
            cliente_id = item["cliente"]["id"]
            cliente_info = item["cliente"]
            servicio_info = item["servicio"]
            monto = item["monto"]
            estado = item["estado"]

            if cliente_id not in clientes_dict:
                clientes_dict[cliente_id] = {
                    "info": cliente_info,
                    "servicios": [],
                    "total": 0
                }

            clientes_dict[cliente_id]["servicios"].append(

                f"- {servicio_info['nombre']}: ${servicio_info['precio']:.2f} → A pagar este mes: ${monto:.2f}"
            )
            clientes_dict[cliente_id]["total"] += monto

        enviados = []

        # Enviar resumen a cada cliente
        for cliente_id, data in clientes_dict.items():
            cliente = self.db.query(ClientesModel).filter_by(id=cliente_id).first()
            if not cliente:
                continue

            resumen = self.generar_resumen_cliente(data, datos_empresa)

            # Método de aviso
            metodo = (cliente.metodo_aviso or "ambos").lower()

            if metodo in ["mail", "ambos"] and cliente.correo:
                self.enviar_por_mail(
                destinatario=cliente.correo,
                resumen=resumen,
                background_tasks=background_tasks
            )
                # self.enviar_por_mail(cliente.correo, resumen)

                # else:
                #     print(f"[WARN] Cliente {cliente.nombre} {cliente.apellido} no tiene correo definido")

            # if metodo in ["whatsapp", "ambos"]:
            #     if cliente.whatsapp:
            #         self.enviar_por_whatsapp(cliente.whatsapp, resumen)
            #     else:
            #         print(f"[WARN] Cliente {cliente.nombre} {cliente.apellido} no tiene WhatsApp definido")

            enviados.append(cliente.nombre + " " + cliente.apellido)

        print(f"✅ Resúmenes enviados: {len(enviados)} clientes")
        return enviados
    

    def generar_resumen_cliente(self, data, datos_empresa):
        cliente = data["info"]
        servicios_txt = "\n".join(data["servicios"])
        total = data["total"]

        resumen = f"""
📋 *Resumen de Pago - {cliente['empresa']}*

👤 Cliente: {cliente['nombre']} {cliente['apellido']}
🏢 Empresa: {cliente['empresa']}

🧾 Servicios:
{servicios_txt}

💰 Total a pagar este mes: ${total:.2f}

🏦 Formas de pago:
- CBU: {datos_empresa.cbu or 'No disponible'}
- CVU: {datos_empresa.cvu or 'No disponible'}
- Otros: {datos_empresa.formas_pago or 'No especificados'}

Gracias por su confianza.
        """
        return resumen.strip()


    # Envio de mails
    def enviar_por_mail(self, destinatario:str, resumen:str, background_tasks: BackgroundTasks):
        message = MessageSchema(
            subject="Resumen mensual de pagos",
            recipients=[destinatario],
            body=resumen,
            subtype=MessageType.plain  # podés usar html más adelante
        )
        background_tasks.add_task(
            fast_mail.send_message,
            message
        )

        # print(f"[MAIL] Enviando a {correo}:\n{mensaje}\n{'-'*60}")

    # def enviar_por_whatsapp(self, numero, mensaje):
    #     print(f"[WHATSAPP] Enviando a {numero}:\n{mensaje}\n{'-'*60}")

