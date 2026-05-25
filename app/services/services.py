from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.models import Calle, Espacio, Ocupacion, EstadoEspacio
from app.schemas.schemas import (
    CalleCreate, CalleUpdate,
    EspacioCreate, EspacioUpdate,
    OcupacionCreate,
)
from fastapi import HTTPException

def crear_calle(db: Session, data: CalleCreate) -> Calle:
    existente = db.query(Calle).filter(Calle.nombre == data.nombre).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe una calle con ese nombre")
    calle = Calle(**data.model_dump())
    db.add(calle)
    db.commit()
    db.refresh(calle)
    return calle

def obtener_calles(db: Session) -> list[Calle]:
    return db.query(Calle).all()

def obtener_calle(db: Session, calle_id: int) -> Calle:
    calle = db.query(Calle).filter(Calle.id == calle_id).first()
    if not calle:
        raise HTTPException(status_code=404, detail="Calle no encontrada")
    return calle

def actualizar_calle(db: Session, calle_id: int, data: CalleUpdate) -> Calle:
    calle = obtener_calle(db, calle_id)
    for campo, valor in data.model_dump(exclude_none=True).items():
        setattr(calle, campo, valor)
    db.commit()
    db.refresh(calle)
    return calle

def crear_espacio(db: Session, data: EspacioCreate) -> Espacio:
    obtener_calle(db, data.calle_id)  # valida que la calle exista
    duplicado = db.query(Espacio).filter(
        Espacio.numero == data.numero,
        Espacio.calle_id == data.calle_id
    ).first()
    if duplicado:
        raise HTTPException(status_code=400, detail="Ya existe ese número en la calle indicada")
    espacio = Espacio(**data.model_dump())
    db.add(espacio)
    db.commit()
    db.refresh(espacio)
    return espacio

def obtener_espacios(db: Session) -> list[Espacio]:
    return db.query(Espacio).all()


def obtener_espacio(db: Session, espacio_id: int) -> Espacio:
    espacio = db.query(Espacio).filter(Espacio.id == espacio_id).first()
    if not espacio:
        raise HTTPException(status_code=404, detail="Espacio no encontrado")
    return espacio

def obtener_espacio_por_calle_numero(db: Session, calle: str, numero: int) -> Espacio:
    calle_db = db.query(Calle).filter(Calle.nombre == calle).first()
    if not calle_db:
        raise HTTPException(status_code=404, detail="Calle no encontrada")
    espacio = db.query(Espacio).filter(Espacio.calle_id == calle_db.id, Espacio.numero == numero).first()
    if not espacio:
        raise HTTPException(status_code=404, detail="Espacio no encontrado")
    return espacio


def actualizar_espacio(db: Session, espacio_id: int, data: EspacioUpdate) -> Espacio:
    espacio = obtener_espacio(db, espacio_id)
    for campo, valor in data.model_dump(exclude_none=True).items():
        setattr(espacio, campo, valor)
    db.commit()
    db.refresh(espacio)
    return espacio

def _hay_conflicto(db: Session, espacio_id: int, inicio: datetime, fin: datetime) -> bool:
    """Verifica si un espacio tiene ocupaciones activas que se solapan con el rango dado."""
    query = db.query(Ocupacion).filter(
        Ocupacion.espacio_id == espacio_id,
        # Hay solapamiento si: inicio_existente < fin_nuevo AND fin_existente > inicio_nuevo
        Ocupacion.inicio_reserva < fin,
    )

    ocupaciones = query.all()
    for oc in ocupaciones:
        if oc.fin_previsto > inicio:
            return True
    return False


def registrar_ocupacion(db: Session, data: OcupacionCreate) -> Ocupacion:
    espacio = obtener_espacio_por_calle_numero(db, data.calle, data.numero_espacio)

    if espacio.estado == EstadoEspacio.inhabilitado:
        raise HTTPException(status_code=400, detail="El espacio está inhabilitado")

    fin_previsto = data.inicio_reserva + timedelta(hours=data.duracion_prevista_hs)

    if _hay_conflicto(db, espacio.id, data.inicio_reserva, fin_previsto):
        raise HTTPException(status_code=409, detail="El espacio ya está ocupado en ese rango horario")

    ocupacion = Ocupacion(**data.model_dump())
    espacio.estado = EstadoEspacio.ocupado
    db.add(ocupacion)
    db.commit()
    db.refresh(ocupacion)
    return ocupacion

def finalizar_ocupacion(db: Session, ocupacion_id: int, fin_real: datetime) -> Ocupacion:
    ocupacion = db.query(Ocupacion).filter(Ocupacion.id == ocupacion_id).first()
    if not ocupacion:
        raise HTTPException(status_code=404, detail="Ocupación no encontrada")
    if ocupacion.fin_real is not None:
        raise HTTPException(status_code=400, detail="La ocupación ya fue finalizada")
    if fin_real < ocupacion.inicio_reserva:
        raise HTTPException(status_code=400, detail="El fin real no puede ser anterior al inicio")

    ocupacion.fin_real = fin_real

    ocupacion.espacio.estado = EstadoEspacio.disponible

    db.commit()
    db.refresh(ocupacion)
    return ocupacion

def obtener_ocupaciones(db: Session, chapa: str | None = None) -> list[Ocupacion]:
    query = db.query(Ocupacion)
    if chapa:
        query = query.filter(Ocupacion.chapa == chapa.upper())
    return query.order_by(Ocupacion.inicio_reserva.desc()).all()


def obtener_ocupacion(db: Session, ocupacion_id: int) -> Ocupacion:
    oc = db.query(Ocupacion).filter(Ocupacion.id == ocupacion_id).first()
    if not oc:
        raise HTTPException(status_code=404, detail="Ocupación no encontrada")
    return oc

def consultar_disponibles(db: Session, desde: datetime, hasta: datetime) -> list[Espacio]:
    # Calcula el fin previsto dentro de SQL sumando los minutos al inicio
    fin_previsto_expr = Ocupacion.inicio_reserva + func.make_interval(0, 0, 0, 0, Ocupacion.duracion_prevista_hs, 0, 0)

    # IDs de espacios que tienen solapamiento en el rango pedido
    ids_ocupados = (
        db.query(Ocupacion.espacio_id)
        .filter(
            Ocupacion.fin_real == None,
            Ocupacion.inicio_reserva < hasta,       # la ocupación empieza antes de que termine el rango
            fin_previsto_expr > desde,      # la ocupación termina después de que empiece el rango
        )
        .distinct()
    )

    return db.query(Espacio).filter(
        Espacio.estado != EstadoEspacio.inhabilitado,
        ~Espacio.id.in_(ids_ocupados)
    ).all()