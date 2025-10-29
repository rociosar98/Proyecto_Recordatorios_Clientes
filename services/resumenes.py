from sqlalchemy.orm import Session, joinedload
from models.clientes import Clientes as ClientesModel
from models.servicios import ServiciosCliente as ServiciosClienteModel
from models.servicios import Servicios as ServicioModel
from models.pagos import Pagos as PagoModel
from models.datos_empresa import DatosEmpresa as DatosEmpresaModel
from datetime import date


class ResumenesService:

    def __init__(self, db) -> None:
        self.db = db

    #def __init__(self, db: Session):
    #    self.db = db

    def enviar_resumenes(self):
        clientes = self.db.query(ClientesModel).options(
            joinedload(ClientesModel.servicios).joinedload(ServiciosClienteModel.servicio)
        ).filter(ClientesModel.activo == True).all()

        datos_empresa = self.db.query(DatosEmpresaModel).first()

        enviados = []

        for cliente in clientes:
            resumen = self._generar_resumen_cliente(cliente, datos_empresa)

            # Simulamos envío según método de aviso
            if cliente.metodo_aviso in ["mail", "ambos"]:
                if cliente.correo:
                    self.enviar_por_mail(cliente.correo, resumen)
                else:
                    print(f"[WARN] Cliente {cliente.nombre} {cliente.apellido} no tiene correo definido")

            if cliente.metodo_aviso in ["whatsapp", "ambos"]:
                if cliente.whatsapp:
                    self.enviar_por_whatsapp(cliente.whatsapp, resumen)
                else:
                    print(f"[WARN] Cliente {cliente.nombre} {cliente.apellido} no tiene WhatsApp definido")


            # Según el método de aviso, se simula el envío
            #if cliente.metodo_aviso in ["mail", "ambos"]:
            #    self.enviar_por_mail(cliente.correo, resumen)

            #if cliente.metodo_aviso in ["whatsapp", "ambos"]:
            #    self.enviar_por_whatsapp(cliente.whatsapp, resumen)

            enviados.append(cliente.nombre + " " + cliente.apellido)

        return enviados

    def _generar_resumen_cliente(self, cliente, datos_empresa):
        servicios = [sc for sc in cliente.servicios if sc.activo]
        total_deuda = 0
        conceptos = []

        for sc in servicios:
            pagado = sum(p.monto for p in sc.pagos)
            deuda = max(sc.precio_congelado - pagado, 0)
            total_deuda += deuda

            conceptos.append(f"{sc.servicio.nombre}: ${sc.precio_congelado:.2f} (Pagado: ${pagado:.2f})")

        resumen = f"""
        📋 *Resumen de Pago*

        👤 Cliente: {cliente.nombre} {cliente.apellido}
        🏢 Empresa: {cliente.empresa}

        🧾 Servicios:
        {chr(10).join(conceptos)}

        💰 Total a pagar: ${total_deuda:.2f}

        🏦 Formas de pago:
        - CBU: {datos_empresa.cbu}
        - CVU: {datos_empresa.cvu}
        - Otros: {datos_empresa.formas_pago or 'No especificados'}

        Muchas gracias por su confianza.
        """

        return resumen

    def enviar_por_mail(self, correo, mensaje):
        print(f"[MAIL] Enviando a {correo}:\n{mensaje}")

    def enviar_por_whatsapp(self, numero, mensaje):
        print(f"[WHATSAPP] Enviando a {numero}:\n{mensaje}")
