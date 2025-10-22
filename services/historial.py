from models.clientes import Clientes as ClientesModel
from schemas.pagos import EntradaPagoOut
from typing import Optional
from models.pagos import Pagos as PagosModel
from models.servicios import ServiciosCliente as ServiciosClienteModel
from datetime import date
from datetime import timedelta
from sqlalchemy import extract
from sqlalchemy.orm import joinedload


class HistorialService:

    def __init__(self, db) -> None:
        self.db = db

    #def __init__(self, db: Session):
    #    self.db = db


    def obtener_historial(self, cliente_id: Optional[int] = None):
        query = (
            self.db.query(PagosModel)
            .join(ServiciosClienteModel)
            .options(
                joinedload(PagosModel.servicio_cliente).joinedload(ServiciosClienteModel.cliente),
                joinedload(PagosModel.servicio_cliente).joinedload(ServiciosClienteModel.servicio)
            )
        )

        if cliente_id:
            query = query.filter(ServiciosClienteModel.cliente_id == cliente_id)

        pagos = query.all()

        resultado = []
        for pago in pagos:
            pagos_relacionados = self.db.query(PagosModel).filter_by(servicio_cliente_id = pago.servicio_cliente_id).all()
            total_pagado = sum(p.monto for p in pagos_relacionados)

            monto_total = pago.servicio_cliente.precio_congelado

            print(f"ServicioClienteID: {pago.servicio_cliente_id}, Total pagado: {total_pagado}, Monto total: {monto_total}")

            if total_pagado >= monto_total:
                estado = "pagado"
            elif total_pagado > 0:
                estado = "parcial"
            else:
                estado = "pendiente"

            resultado.append({
                "monto": pago.monto,
                "fecha_facturacion": pago.fecha_facturacion,
                "fecha_pago": pago.fecha_pago,
                "estado": estado,
                "cliente": pago.servicio_cliente.cliente.nombre,
                "servicio": pago.servicio_cliente.servicio.nombre
            })

        return resultado



        #pagos = (
        #    self.db.query(PagosModel)
        #    .join(ServiciosClienteModel)
        #    .filter(ServiciosClienteModel.cliente_id == cliente_id)
        #    .order_by(PagosModel.fecha_facturacion.desc())
            #.filter(PagosModel.servicio_cliente_id == servicio_cliente_id)
        #    .all()
        #)
        #return pagos
    

    #def obtener_historial(self, cliente_id: int):
    #    consumos = self.db.query(ConsumoModel).filter_by(cliente_id=cliente_id).all()
    #    pagos = (
    #        self.db.query(PagosModel)
    #        .join(ServiciosClienteModel)
    #        .filter(ServiciosClienteModel.cliente_id == cliente_id)
    #        .all()
    #    )
        
    #    historial = {
    #        "consumos": [
    #            {
    #                "fecha_facturacion": c.fecha_facturacion,
    #                "detalle": c.detalle,
    #                "monto": c.monto,
    #            }
    #            for c in consumos
    #        ],
    #        "pagos": [
    #            {
    #                "fecha_pago": p.fecha,
    #                "monto": p.monto,
    #                "servicio": p.servicio_cliente.servicio.nombre,
    #            }
    #            for p in pagos
    #        ],
    #    }
    #    return historial

    #def listar_por_filtros(self, fecha: date, condicion_iva: Optional[str], responsable_cuenta: Optional[str]):
    #    query = self.db.query(ServiciosClienteModel).filter(
    #        ServiciosClienteModel.fecha_facturacion == fecha
    #    )
    #    if condicion_iva:
    #        query = query.join(ClientesModel).filter(ClientesModel.condicion_iva == condicion_iva)
    #    if responsable_cuenta:
    #        query = query.filter(ServiciosClienteModel.responsable_cuenta == responsable_cuenta)
    #    resultados = query.all()
    #    return [s.to_dict() for s in resultados]  # Asumiendo que tienes método to_dict()
    

    def listar_por_filtros(self, condicion_iva: Optional[str], responsable_cuenta: Optional[str]):
        query = (
            self.db.query(PagosModel)
            .join(ServiciosClienteModel, PagosModel.servicio_cliente_id == ServiciosClienteModel.id)
            .join(ClientesModel, ServiciosClienteModel.cliente_id == ClientesModel.id)
            .options(
                joinedload(PagosModel.servicio_cliente)
                .joinedload(ServiciosClienteModel.cliente)
                .joinedload(ClientesModel.responsable)
            )
        )

        if condicion_iva:
            query = query.filter(ClientesModel.condicion_iva == condicion_iva)

        if responsable_cuenta:
            query = query.filter(ClientesModel.responsable_id == responsable_cuenta)

        pagos = query.all()

        resultados = []
        for pago in pagos:
            resultados.append({
                "id": pago.id,
                "servicio_cliente_id": pago.servicio_cliente_id,
                "monto": pago.monto,
                "fecha_facturacion": pago.fecha_facturacion,
                "fecha_pago": pago.fecha_pago,
                "estado": pago.estado.value,
                "observaciones": pago.observaciones,
                "cliente": {
                    "id": pago.servicio_cliente.cliente.id,
                    "nombre": pago.servicio_cliente.cliente.nombre,
                    "empresa": pago.servicio_cliente.cliente.empresa,
                    "condicion_iva": pago.servicio_cliente.cliente.condicion_iva,
                    "responsable": {
                        "id": pago.servicio_cliente.cliente.responsable.id,
                        "nombre": pago.servicio_cliente.cliente.responsable.nombre,
                        "apellido": pago.servicio_cliente.cliente.responsable.apellido
                    } if pago.servicio_cliente.cliente.responsable else None
                },
                "servicio": {
                    "id": pago.servicio_cliente.servicio.id,
                    "nombre": pago.servicio_cliente.servicio.nombre
                }
            })

        return resultados



    # def listar_entradas(self, fecha_inicio: Optional[date], fecha_fin: Optional[date], periodo: Optional[str]):
    #     query = self.db.query(PagosModel).options(
    #         joinedload(PagosModel.servicio_cliente)
    #         .joinedload(ServiciosClienteModel.cliente),
    #         joinedload(PagosModel.servicio_cliente)
    #         .joinedload(ServiciosClienteModel.servicio)
    #     )

    #     # Filtros por período
    #     if periodo == "mensual":
    #         hoy = date.today()
    #         inicio_mes = hoy.replace(day=1)
    #         query = query.filter(PagosModel.fecha_facturacion >= inicio_mes)
    #     elif periodo == "anual":
    #         hoy = date.today()
    #         inicio_anio = hoy.replace(month=1, day=1)
    #         query = query.filter(PagosModel.fecha_facturacion >= inicio_anio)
    #     else:
    #         if fecha_inicio:
    #             query = query.filter(PagosModel.fecha_facturacion >= fecha_inicio)
    #         if fecha_fin:
    #             query = query.filter(PagosModel.fecha_facturacion <= fecha_fin)

    #     pagos = query.all()

    #     # Formatear respuesta enriquecida
    #     resultado = []
    #     for pago in pagos:
    #         cliente = pago.servicio_cliente.cliente
    #         servicio = pago.servicio_cliente.servicio

    #         resultado.append({
    #             "cliente": f"{cliente.nombre} {cliente.apellido}",
    #             "empresa": cliente.empresa,
    #             "servicio": servicio.nombre,
    #             "monto": pago.monto,
    #             "fecha_facturacion": pago.fecha_facturacion,
    #             "fecha_pago": pago.fecha_pago,
    #             "estado": pago.estado.value,
    #             "observaciones": pago.observaciones
    #         })

    #     return resultado

    

    def listar_entradas(self, periodo: Optional[str], anio: Optional[int], mes: Optional[int], fecha_inicio: Optional[date], fecha_fin: Optional[date]):
        query = self.db.query(PagosModel)

        if periodo == "mensual":
            inicio = date(anio, mes, 1)
            if mes == 12:
                fin = date(anio + 1, 1, 1)
            else:
                fin = date(anio, mes + 1, 1)
            query = query.filter(PagosModel.fecha_facturacion >= inicio, PagosModel.fecha_facturacion < fin)

        elif periodo == "anual":
            inicio = date(anio, 1, 1)
            fin = date(anio + 1, 1, 1)
            query = query.filter(PagosModel.fecha_facturacion >= inicio, PagosModel.fecha_facturacion < fin)

        else:
            # Rango personalizado
            query = query.filter(PagosModel.fecha_facturacion >= fecha_inicio, PagosModel.fecha_facturacion <= fecha_fin)

        return query.all()

    

    #def listar_entradas(self, fecha_inicio: Optional[date], fecha_fin: Optional[date], periodo: Optional[str]):
    #    query = self.db.query(PagosModel)

    #    if periodo == "mensual":
    #        hoy = date.today()
    #        inicio_mes = hoy.replace(day=1)
    #        query = query.filter(PagosModel.fecha >= inicio_mes)
    #    elif periodo == "anual":
    #        hoy = date.today()
    #        inicio_anio = hoy.replace(month=1, day=1)
    #        query = query.filter(PagosModel.fecha >= inicio_anio)
    #    else:
    #        if fecha_inicio:
    #            query = query.filter(PagosModel.fecha >= fecha_inicio)
    #        if fecha_fin:
    #            query = query.filter(PagosModel.fecha <= fecha_fin)

    #    return query.all()
