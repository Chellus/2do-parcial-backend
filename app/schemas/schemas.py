from datetime import datetime
from pydantic import BaseModel, field_validator
from app.models.models import EstadoEspacio, Calle

class CalleCreate(BaseModel):
    nombre: str


class CalleUpdate(BaseModel):
    nombre: str | None = None


class CalleOut(BaseModel):
    id: int
    nombre: str

    model_config = {"from_attributes": True}

class EspacioCreate(BaseModel):
    numero: int
    calle_id: int
    duracion_min_hs: int | None = None
    duracion_max_hs: int | None = None

    @field_validator("numero")
    @classmethod
    def numero_positivo(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("El número de espacio debe ser positivo")
        return v


class EspacioUpdate(BaseModel):
    estado: EstadoEspacio | None = None
    duracion_min_hs: int | None = None
    duracion_max_hs: int | None = None

class EspacioOut(BaseModel):
    id: int
    numero: int
    calle_id: int
    estado: EstadoEspacio
    calle: str
    duracion_min_hs: int
    duracion_max_hs: int

    model_config = {"from_attributes": True}

    @field_validator("calle", mode="before")
    @classmethod
    def convertir_calle(cls, v):
        if isinstance(v, Calle):
            return v.nombre
        return v

class OcupacionCreate(BaseModel):
    calle: str
    numero_espacio: int
    chapa: str
    inicio_reserva: datetime
    duracion_prevista_hs: int

    @field_validator("duracion_prevista_hs")
    @classmethod
    def duracion_valida(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("La duración debe ser mayor a 0 hs")
        return v

class OcupacionFinalizarIn(BaseModel):
    fin_real: datetime

class OcupacionOut(BaseModel):
    id: int
    espacio_id: int
    chapa: str
    inicio_reserva: datetime
    duracion_prevista_hs: int
    fin_previsto: datetime
    fin_real: datetime | None
    calle: str
    numero: int

    model_config = {"from_attributes": True}

class DisponibilidadQuery(BaseModel):
    desde: datetime
    hasta: datetime

    @field_validator("hasta")
    @classmethod
    def hasta_mayor_que_desde(cls, v: datetime, info) -> datetime:
        if "desde" in info.data and v <= info.data["desde"]:
            raise ValueError("'hasta' debe ser posterior a 'desde'")
        return v
