from sqlalchemy.orm import Session, joinedload
from models.clientes import Clientes as ClientesModel
from models.servicios import ServiciosCliente as ServiciosClienteModel
from models.servicios import Servicios as ServicioModel
from models.pagos import Pagos as PagoModel
from models.datos_empresa import DatosEmpresa as DatosEmpresaModel
from models.listado_mensual import ListadoMensual as ListadoMensualModel
from datetime import date


class ResumenesService:

    def __init__(self, db) -> None:
        self.db = db
        

    def enviar_resumenes(self):
        # 📅 Obtener el último listado mensual
        listado = (
            self.db.query(ListadoMensualModel)
            .order_by(ListadoMensualModel.fecha.desc())
            .first()
        )

        if not listado or not listado.contenido:
            print("⚠️ No hay listado mensual generado para enviar.")
            return []

        # 🏦 Datos de la empresa (CBU, CVU, etc.)
        datos_empresa = self.db.query(DatosEmpresaModel).first()
        if not datos_empresa:
            print("⚠️ No hay datos de empresa configurados.")
            return []

        # 📊 Agrupar servicios por cliente
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
                #f"- {servicio_info['nombre']}: ${servicio_info['precio']:.2f} "
                #f"→ A pagar este mes: ${monto:.2f})"

                f"- {servicio_info['nombre']}: ${servicio_info['precio']:.2f} → A pagar este mes: ${monto:.2f}"
            )
            clientes_dict[cliente_id]["total"] += monto

        enviados = []

        # 📤 Enviar resumen a cada cliente
        for cliente_id, data in clientes_dict.items():
            cliente = self.db.query(ClientesModel).filter_by(id=cliente_id).first()
            if not cliente:
                continue

            resumen = self.generar_resumen_cliente(data, datos_empresa)

            # Método de aviso
            metodo = (cliente.metodo_aviso or "ambos").lower()

            if metodo in ["mail", "ambos"]:
                if cliente.correo:
                    self.enviar_por_mail(cliente.correo, resumen)
                else:
                    print(f"[WARN] Cliente {cliente.nombre} {cliente.apellido} no tiene correo definido")

            if metodo in ["whatsapp", "ambos"]:
                if cliente.whatsapp:
                    self.enviar_por_whatsapp(cliente.whatsapp, resumen)
                else:
                    print(f"[WARN] Cliente {cliente.nombre} {cliente.apellido} no tiene WhatsApp definido")

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


    # 🔹 Métodos simulados de envío (puedes reemplazarlos por los reales)
    def enviar_por_mail(self, correo, mensaje):
        print(f"[MAIL] Enviando a {correo}:\n{mensaje}\n{'-'*60}")

    def enviar_por_whatsapp(self, numero, mensaje):
        print(f"[WHATSAPP] Enviando a {numero}:\n{mensaje}\n{'-'*60}")


    # def enviar_resumenes(self):
    #     clientes = self.db.query(ClientesModel).options(
    #         joinedload(ClientesModel.servicios).joinedload(ServiciosClienteModel.servicio)
    #     ).filter(ClientesModel.activo == True).all()

    #     datos_empresa = self.db.query(DatosEmpresaModel).first()

    #     enviados = []

    #     for cliente in clientes:
    #         resumen = self.generar_resumen_cliente(cliente, datos_empresa)

    #         # Simulamos envío según método de aviso
    #         if cliente.metodo_aviso in ["mail", "ambos"]:
    #             if cliente.correo:
    #                 self.enviar_por_mail(cliente.correo, resumen)
    #             else:
    #                 print(f"[WARN] Cliente {cliente.nombre} {cliente.apellido} no tiene correo definido")

    #         if cliente.metodo_aviso in ["whatsapp", "ambos"]:
    #             if cliente.whatsapp:
    #                 self.enviar_por_whatsapp(cliente.whatsapp, resumen)
    #             else:
    #                 print(f"[WARN] Cliente {cliente.nombre} {cliente.apellido} no tiene WhatsApp definido")

            ## Según el método de aviso, se simula el envío
            ##if cliente.metodo_aviso in ["mail", "ambos"]:
            ##    self.enviar_por_mail(cliente.correo, resumen)

            ##if cliente.metodo_aviso in ["whatsapp", "ambos"]:
            ##    self.enviar_por_whatsapp(cliente.whatsapp, resumen)

        #     enviados.append(cliente.nombre + " " + cliente.apellido)

        # return enviados

    # def generar_resumen_cliente(self, cliente, datos_empresa):
    #     servicios = [sc for sc in cliente.servicios if sc.activo]
    #     total_deuda = 0
    #     conceptos = []

    #     for sc in servicios:
    #         pagado = sum(p.monto for p in sc.pagos)
    #         deuda = max(sc.precio_congelado - pagado, 0)
    #         total_deuda += deuda

    #         conceptos.append(f"{sc.servicio.nombre}: ${sc.precio_congelado:.2f} (Pagado: ${pagado:.2f})")

    #     resumen = f"""
    #     📋 *Resumen de Pago*

    #     👤 Cliente: {cliente.nombre} {cliente.apellido}
    #     🏢 Empresa: {cliente.empresa}

    #     🧾 Servicios:
    #     {chr(10).join(conceptos)}

    #     💰 Total a pagar: ${total_deuda:.2f}

    #     🏦 Formas de pago:
    #     - CBU: {datos_empresa.cbu}
    #     - CVU: {datos_empresa.cvu}
    #     - Otros: {datos_empresa.formas_pago or 'No especificados'}

    #     Muchas gracias por su confianza.
    # #     """

    #     return resumen

    # def enviar_por_mail(self, correo, mensaje):
    #     print(f"[MAIL] Enviando a {correo}:\n{mensaje}")

    # def enviar_por_whatsapp(self, numero, mensaje):
    #     print(f"[WHATSAPP] Enviando a {numero}:\n{mensaje}")
