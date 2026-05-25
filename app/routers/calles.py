from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.schemas import CalleCreate, CalleUpdate, CalleOut
from app.services import services

router = APIRouter(prefix="/calles", tags=["Calles"])


@router.post("/", response_model=CalleOut, status_code=201)
def crear_calle(data: CalleCreate, db: Session = Depends(get_db)):
    return services.crear_calle(db, data)


@router.get("/", response_model=list[CalleOut])
def listar_calles(
    nombre: str | None = Query(default=None, description="Filtrar por nombre de calle"),
    db: Session = Depends(get_db),
):
    return services.obtener_calles(db, nombre)


@router.get("/{calle_id}", response_model=CalleOut)
def obtener_calle(calle_id: int, db: Session = Depends(get_db)):
    return services.obtener_calle(db, calle_id)


@router.patch("/{calle_id}", response_model=CalleOut)
def actualizar_calle(calle_id: int, data: CalleUpdate, db: Session = Depends(get_db)):
    return services.actualizar_calle(db, calle_id, data)
