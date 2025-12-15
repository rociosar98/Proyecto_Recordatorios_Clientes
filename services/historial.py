from models.clientes import Clientes as ClientesModel
from schemas.pagos import EntradaPagoOut
from typing import Optional
from models.pagos import Pagos as PagosModel
from models.servicios import Servicios as ServiciosModel, ServiciosCliente as ServiciosClienteModel
from models.usuarios import Usuarios as UsuariosModel
from datetime import date, datetime
from sqlalchemy.orm import joinedload
from sqlalchemy import extract


def meses_de_recurrencia(tipo: str) -> int:
    mapping = {
        "mensual": 1,
        "bimestral": 2,
        "trimestral": 3,
        "cuatrimestral": 4,
        "semestral": 6,
        "anual": 12
    }
    return mapping.get(tipo.lower(), 1)

def toca_facturar(servicio_cliente, anio: int, mes: int) -> bool:
    """Devuelve True si el servicio toca facturar este mes."""
    fecha_inicio = servicio_cliente.fecha_inicio
    meses_transcurridos = (anio - fecha_inicio.year) * 12 + (mes - fecha_inicio.month)

    # Si tiene cuotas → se factura mientras no se cumplan todas
    if servicio_cliente.cuotas:
        return meses_transcurridos < servicio_cliente.cuotas

    # Si tiene recurrencia → se factura según el intervalo correspondiente
    if servicio_cliente.servicio.recurrencia:
        recurrencia_meses = meses_de_recurrencia(servicio_cliente.servicio.recurrencia.value)
        return meses_transcurridos % recurrencia_meses == 0

    # Otros casos: siempre facturar
    return True


class HistorialService:

    def __init__(self, db) -> None:
        self.db = db


    def obtener_historial(self, cliente_id: Optional[int] = None):
        query = (
            self.db.query(PagosModel)
            .join(ServiciosClienteModel)
            .options(
                joinedload(PagosModel.servicio_cliente).joinedload(ServiciosClienteModel.cliente),
                joinedload(PagosModel.servicio_cliente).joinedload(ServiciosClienteModel.servicio)
            )
            .order_by(PagosModel.fecha_facturacion.desc(), PagosModel.fecha_pago.desc())
        )

        if cliente_id:
            query = query.filter(ServiciosClienteModel.cliente_id == cliente_id)

        pagos = query.all()

        resultado = []

        for pago in pagos:
            pagos_relacionados = (
                self.db.query(PagosModel)
                .filter_by(servicio_cliente_id=pago.servicio_cliente_id)
                .all()
            )
            total_pagado = sum(p.monto for p in pagos_relacionados)
            monto_total = pago.servicio_cliente.precio_congelado

            # Determinar estado del pago
            if total_pagado >= monto_total:
                estado = "pagado"
            elif total_pagado > 0:
                estado = "parcial"
            else:
                estado = "pendiente"

            cliente = pago.servicio_cliente.cliente
            servicio = pago.servicio_cliente.servicio

            resultado.append({
                "monto": pago.monto,
                "fecha_facturacion": pago.fecha_facturacion,
                "fecha_pago": pago.fecha_pago,
                "estado": estado,
                "cliente": {
                    "id": cliente.id,
                    "nombre": cliente.nombre,
                    "apellido": cliente.apellido,
                    "empresa": cliente.empresa,
                    "condicion_iva": cliente.condicion_iva,
                },
                #"servicio": {
                #    "id": servicio.id,
                #    "nombre": servicio.nombre,
                "servicio": pago.servicio_cliente.servicio.nombre
                #}
            })

        return resultado
    

    def listado_mensual(self, anio: int, mes: int, condicion_iva: str = None,
                            responsable_nombre: str = None):

            query = (
                self.db.query(ServiciosClienteModel)
                .join(ClientesModel, ServiciosClienteModel.cliente_id == ClientesModel.id)
                .join(ServiciosModel, ServiciosClienteModel.servicio_id == ServiciosModel.id)
                .join(UsuariosModel, ClientesModel.responsable_id == UsuariosModel.id, isouter=True)
                .options(
                    joinedload(ServiciosClienteModel.cliente)
                    .joinedload(ClientesModel.responsable),
                    joinedload(ServiciosClienteModel.servicio),
                    joinedload(ServiciosClienteModel.pagos)
                )
                .filter(
                    ServiciosClienteModel.activo == True,
                    extract('year', ServiciosClienteModel.fecha_inicio) <= anio,
                    extract('month', ServiciosClienteModel.fecha_inicio) <= mes
                )
            )

            if condicion_iva:
                query = query.filter(ClientesModel.condicion_iva == condicion_iva)

            if responsable_nombre:
                nombre_completo = (UsuariosModel.nombre + " " + UsuariosModel.apellido)
                query = query.filter(nombre_completo.ilike(f"%{responsable_nombre}%"))

            servicios_cliente = query.all()

            resultados = []
            primer_dia_mes = date(anio, mes, 1)
            ultimo_dia_mes = date(anio, mes + 1, 1) if mes < 12 else date(anio + 1, 1, 1)

            for sc in servicios_cliente:
                # Verificamos si toca facturar este mes
                if not toca_facturar(sc, anio, mes):
                    continue

                pagos = sc.pagos or []

                # Pagos anteriores al mes actual
                pagos_anteriores = [
                    p for p in pagos if p.fecha_facturacion and p.fecha_facturacion < primer_dia_mes
                ]
                total_pagado_anteriores = sum(p.monto for p in pagos_anteriores)

                # Saldo a favor acumulado (pagos de más en meses previos)
                saldo_a_favor = max(0, total_pagado_anteriores - sc.precio_congelado)

                # Pagos realizados dentro del mes actual
                pagos_mes = [
                    p for p in pagos
                    if p.fecha_facturacion and primer_dia_mes <= p.fecha_facturacion < ultimo_dia_mes
                ]
                total_pagado_mes = sum(p.monto for p in pagos_mes)

                # Total pagado desde que empezó el servicio
                #total_pagado = sum(p.monto for p in pagos)

                # Monto a facturar este mes (restando saldo previo y pagos actuales)
                monto_a_mostrar = max(0, sc.precio_congelado - total_pagado_mes - saldo_a_favor)

                saldo_mes = monto_a_mostrar

                # monto_a_mostrar = max(0, sc.precio_congelado - total_pagado_mes - max(0, total_pagado_anteriores - sc.precio_congelado))

                # Determinar estado
                if monto_a_mostrar == 0:
                    estado = "pagado"
                #elif monto_a_mostrar < sc.precio_congelado:
                elif total_pagado_mes > 0 or saldo_a_favor > 0:
                    estado = "parcial"
                else:
                    estado = "pendiente"

                resultados.append({
                    "servicio_cliente_id": sc.id,
                    "cliente": {
                        "id": sc.cliente.id,
                        "nombre": sc.cliente.nombre,
                        "apellido": sc.cliente.apellido,
                        "empresa": sc.cliente.empresa,
                        "condicion_iva": sc.cliente.condicion_iva,
                        "responsable": {
                            "id": sc.cliente.responsable.id if sc.cliente.responsable else None,
                            "nombre": sc.cliente.responsable.nombre if sc.cliente.responsable else None,
                            "apellido": sc.cliente.responsable.apellido if sc.cliente.responsable else None
                        }
                    },
                    "servicio": {
                        "id": sc.servicio.id,
                        "nombre": sc.servicio.nombre,
                        "precio": sc.precio_congelado,
                        "recurrencia": sc.servicio.recurrencia.value if sc.servicio.recurrencia else None,
                        "cuotas": sc.cuotas
                    },
                    "fecha_facturacion": primer_dia_mes,
                    "monto_mes": sc.precio_congelado,
                    "monto": monto_a_mostrar,
                    "total_pagado": total_pagado_mes,  # suma de pagos del mes + saldo previo
                    "saldo_mes": saldo_mes,
                    "saldo_a_favor": saldo_a_favor,
                    "estado": estado
                })

            return resultados
    

    def listado_mensual_actualizado(self, db, anio, mes):
        #"""Devuelve listado mensual con total_pagado, saldo y saldo_a_favor actualizado."""
        servicios = db.query(ServiciosClienteModel).options(joinedload(ServiciosClienteModel.cliente)).all()
        listado = []

        primer_dia_mes = date(anio, mes, 1)
        if mes == 12:
            primer_dia_mes_siguiente = date(anio + 1, 1, 1)
        else:
            primer_dia_mes_siguiente = date(anio, mes + 1, 1)

        for sc in servicios:
            # Traer todos los pagos del cliente/servicio desde la DB
            pagos = (
                db.query(PagosModel)
                .filter(PagosModel.servicio_cliente_id == sc.id)
                .all()
            )

            # Pagos anteriores al mes actual
            pagos_anteriores = [p for p in pagos if p.fecha_facturacion < primer_dia_mes]
            total_pagado_anteriores = sum(p.monto for p in pagos_anteriores)

            # Saldo a favor acumulado
            saldo_a_favor = max(0, total_pagado_anteriores - sc.precio_congelado)

            # Pagos dentro del mes actual
            pagos_mes = [p for p in pagos if primer_dia_mes <= p.fecha_facturacion < primer_dia_mes_siguiente]
            total_pagado_mes = sum(p.monto for p in pagos_mes)

            # Monto base del mes
            if sc.cuotas and sc.cuotas > 0:
                monto_mes = max(0, sc.precio_congelado / sc.cuotas - total_pagado_mes - saldo_a_favor)
            else:
                monto_mes = max(0, sc.precio_congelado - total_pagado_mes - saldo_a_favor)

            # Estado
            if monto_mes == 0:
                estado = "pagado"
            elif total_pagado_mes > 0:
                estado = "parcial"
            else:
                estado = "pendiente"

            listado.append({
                "servicio_cliente_id": sc.id,
                "cliente": {
                    "nombre": sc.cliente.nombre,
                    "apellido": sc.cliente.apellido,
                    "empresa": sc.cliente.empresa
                },
                "servicio": {
                    "nombre": sc.servicio.nombre
                },
                "monto_mes": monto_mes,
                "total_pagado_mes": total_pagado_mes,
                "saldo_mes": max(0, monto_mes - total_pagado_mes),
                "saldo_a_favor": saldo_a_favor,
                "estado": estado
            })

        return listado


    # filtrar historial por mes, año, o fecha personalizada
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

    