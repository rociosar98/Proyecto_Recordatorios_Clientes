from enum import Enum

class TipoServicio(str, Enum):
    recurrente = "recurrente"
    pago_unico = "pago_unico"

class Recurrencia (str, Enum):
    mensual = "mensual"
    bimestral = "bimestral"
    trimestral = "trimestral"
    cuatrimestral = "cuatrimestral"
    semestral = "semestral"
    anual = "anual"

class MetodoAviso(str, Enum):
    whatsapp = "whatsapp"
    mail = "mail"
    ambos = "ambos"

class PermisoUsuario(str, Enum):
    lectura = "lectura"
    escritura = "escritura"

class TipoRecordatorio(str, Enum):
    inicial = "inicial"
    recordatorio = "recordatorio"
    mora = "mora"
    corte = "corte"

class EstadoPago(str, Enum):
    pendiente = "pendiente"
    parcial = "parcial"
    pagado = "pagado"