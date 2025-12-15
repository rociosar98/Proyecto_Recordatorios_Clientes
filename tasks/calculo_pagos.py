from datetime import date

def calcular_monto_mes(sc, anio, mes):
    """Unifica el cálculo de montos, saldo a favor, pagos previos y cuotas."""

    pagos = sc.pagos or []

    primer_dia_mes = date(anio, mes, 1)
    if mes == 12:
        ultimo_dia_mes = date(anio + 1, 1, 1)
    else:
        ultimo_dia_mes = date(anio, mes + 1, 1)

    # Pagos anteriores al mes actual
    pagos_anteriores = [
        p for p in pagos if p.fecha_facturacion and p.fecha_facturacion < primer_dia_mes
    ]
    total_pagado_anteriores = sum(p.monto for p in pagos_anteriores)

    # Saldo a favor acumulado
    saldo_a_favor = max(0, total_pagado_anteriores - sc.precio_congelado)

    # Pagos dentro del mes actual
    pagos_mes = [
        p for p in pagos
        if p.fecha_facturacion and primer_dia_mes <= p.fecha_facturacion < ultimo_dia_mes
    ]
    total_pagado_mes = sum(p.monto for p in pagos_mes)

    # Monto base mensual (considerando cuotas)
    if sc.cuotas and sc.cuotas > 0:
        monto_base = sc.precio_congelado / sc.cuotas
    else:
        monto_base = sc.precio_congelado

    # Monto final del mes
    monto_mes = max(0, monto_base - total_pagado_mes - saldo_a_favor)

    # Estado
    if monto_mes == 0:
        estado = "pagado"
    elif total_pagado_mes > 0:
        estado = "parcial"
    else:
        estado = "pendiente"

    return {
        "monto_mes": monto_mes,
        "saldo_a_favor": saldo_a_favor,
        "total_pagado_mes": total_pagado_mes,
        "estado": estado
    }
