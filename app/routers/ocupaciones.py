from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.schemas import OcupacionCreate, OcupacionOut, OcupacionFinalizarIn
from app.services import services

router = APIRouter(prefix="/ocupaciones", tags=["Ocupaciones"])


@router.post("/", response_model=OcupacionOut, status_code=201)
def registrar_ocupacion(data: OcupacionCreate, db: Session = Depends(get_db)):
    return services.registrar_ocupacion(db, data)


@router.get("/", response_model=list[OcupacionOut])
def listar_ocupaciones(
    patente: str | None = Query(default=None, description="Filtrar por patente"),
    db: Session = Depends(get_db),
):
    return services.obtener_ocupaciones(db, patente)


@router.get("/{ocupacion_id}", response_model=OcupacionOut)
def obtener_ocupacion(ocupacion_id: int, db: Session = Depends(get_db)):
    return services.obtener_ocupacion(db, ocupacion_id)


@router.patch("/{ocupacion_id}/finalizar", response_model=OcupacionOut)
def finalizar_ocupacion(ocupacion_id: int, data: OcupacionFinalizarIn, db: Session = Depends(get_db)):
    return services.finalizar_ocupacion(db, ocupacion_id, data.fin_real)
