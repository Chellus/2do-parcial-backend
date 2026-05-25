from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.schemas import EspacioOut
from app.services import services

router = APIRouter(prefix="/disponibilidad", tags=["Disponibilidad"])


@router.get("/", response_model=list[EspacioOut])
def espacios_disponibles(
    desde: datetime = Query(description="Inicio del rango (ISO 8601). Ej: 2026-05-26T08:00:00"),
    hasta: datetime = Query(description="Fin del rango (ISO 8601). Ej: 2026-05-26T10:00:00"),
    calle: str | None = Query(default=None, description="Filtrar por nombre de calle"),
    db: Session = Depends(get_db),
):
    if hasta <= desde:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="'hasta' debe ser posterior a 'desde'")
    return services.consultar_disponibles(db, desde, hasta, calle)
