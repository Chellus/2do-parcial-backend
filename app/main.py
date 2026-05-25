from fastapi import FastAPI
from app.db.database import engine, Base
from app.routers import calles, espacios, ocupaciones, disponibilidad

# Importa los modelos para que SQLAlchemy los registre antes de crear tablas
import app.models.models  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Estacionamiento Tarifado",
    description="API REST para gestión de espacios de estacionamiento en vía pública.",
    version="1.0.0",
)

app.include_router(calles.router)
app.include_router(espacios.router)
app.include_router(ocupaciones.router)
app.include_router(disponibilidad.router)


@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "sistema": "Estacionamiento Tarifado"}
