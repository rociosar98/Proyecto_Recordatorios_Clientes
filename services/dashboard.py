from models.datos_empresa import DatosEmpresa as DatosEmpresaModel
from schemas.datos_empresa import DatosEmpresa
import io
import pandas as pd
from models.pagos import Pagos

class DashboardService:

    def __init__(self, db) -> None:
        self.db = db

    #def __init__(self, db: Session):
    #    self.db = db

    def get_datos_empresa(self) -> DatosEmpresaModel | None:
        return self.db.query(DatosEmpresaModel).first()

    def update_datos_empresa(self, data: DatosEmpresa) -> DatosEmpresaModel:
        datos = self.get_datos_empresa()
        if datos:
            datos.cbu = data.cbu
            datos.cvu = data.cvu
            datos.formas_pago = data.formas_pago
        else:
            datos = DatosEmpresaModel(**data.dict())
            self.db.add(datos)

        self.db.commit()
        self.db.refresh(datos)
        return datos


     # Traer pagos en un rango de fechas
    def get_pagos_por_rango(self, desde, hasta):
        return self.db.query(Pagos).filter(
            Pagos.fecha_facturacion >= desde,
            Pagos.fecha_facturacion <= hasta
        ).all()

    # Generar archivo CSV o Excel
    def generar_archivo(self, pagos, desde, hasta, formato):
        data = []
        for p in pagos:
            cliente = p.cliente.nombre if p.cliente else "-"
            empresa = p.cliente.empresa if p.cliente else "-"
            servicio = p.servicio.nombre if p.servicio else "-"
            data.append({
                "ID": p.id,
                "Cliente": cliente,
                "Empresa": empresa,
                "Servicio": servicio,
                "Monto": p.monto,
                "Fecha Facturación": p.fecha_facturacion,
                "Fecha Pago": p.fecha_pago,
                "Estado": p.estado.value if hasattr(p.estado, "value") else p.estado,
                "Observaciones": p.observaciones or "",
            })

        df = pd.DataFrame(data)
        buffer = io.BytesIO()
        filename = f"pagos_{desde}_{hasta}"

        if formato == "csv":
            df.to_csv(buffer, index=False)
        else:
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False)

        buffer.seek(0)
        return buffer, filename


    # Eliminar pagos en un rango de fechas
    def eliminar_pagos_por_rango(self, desde, hasta):
        pagos_query = self.db.query(Pagos).filter(
            Pagos.fecha_facturacion >= desde,
            Pagos.fecha_facturacion <= hasta
        )
        total = pagos_query.count()
        if total > 0:
            pagos_query.delete(synchronize_session=False)
            self.db.commit()
        return total
    