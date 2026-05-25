from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import EstadoEspacio
from app.schemas.schemas import EspacioCreate, EspacioUpdate, EspacioOut
from app.services import services

router = APIRouter(prefix="/espacios", tags=["Espacios"])


@router.post("/", response_model=EspacioOut, status_code=201)
def crear_espacio(data: EspacioCreate, db: Session = Depends(get_db)):
    return services.crear_espacio(db, data)


@router.get("/", response_model=list[EspacioOut])
def listar_espacios(
    calle: str | None = Query(default=None, description="Filtrar por nombre de calle"),
    estado: EstadoEspacio | None = Query(default=None, description="Filtrar por estado (disponible, ocupado, inhabilitado)"),
    db: Session = Depends(get_db),
):
    return services.obtener_espacios(db, calle, estado)


@router.get("/{espacio_id}", response_model=EspacioOut)
def obtener_espacio(espacio_id: int, db: Session = Depends(get_db)):
    return services.obtener_espacio(db, espacio_id)


@router.patch("/{espacio_id}", response_model=EspacioOut)
def actualizar_espacio(espacio_id: int, data: EspacioUpdate, db: Session = Depends(get_db)):
    return services.actualizar_espacio(db, espacio_id, data)
