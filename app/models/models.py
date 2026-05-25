from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, UniqueConstraint, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.database import Base

class EstadoEspacio(str, enum.Enum):
    disponible = "disponible"
    ocupado = "ocupado"
    inhabilitado = "inhabilitado"


class Calle(Base):
    __tablename__ = "calles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    espacios: Mapped[list["Espacio"]] = relationship("Espacio", back_populates="calle")

class Espacio(Base):
    __tablename__ = "espacios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    numero: Mapped[int] = mapped_column(Integer, nullable=False)
    calle_id: Mapped[int] = mapped_column(Integer, ForeignKey("calles.id"), nullable=False)
    duracion_min_hs: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  
    duracion_max_hs: Mapped[int] = mapped_column(Integer, default=24, nullable=False)
    estado: Mapped[EstadoEspacio] = mapped_column(
        SAEnum(EstadoEspacio), default=EstadoEspacio.disponible, nullable=False
    )

    __table_args__ = (
        UniqueConstraint("numero", "calle_id", name="uq_numero_calle"),
    )

    calle: Mapped["Calle"] = relationship("Calle", back_populates="espacios")
    ocupaciones: Mapped[list["Ocupacion"]] = relationship("Ocupacion", back_populates="espacio")

class Ocupacion(Base):
    __tablename__ = "ocupaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    espacio_id: Mapped[int] = mapped_column(Integer, ForeignKey("espacios.id"), nullable=False)
    chapa: Mapped[str] = mapped_column(String(10), nullable=False)
    inicio_reserva: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duracion_prevista_hs: Mapped[int] = mapped_column(Integer, nullable=False)
    fin_real: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    espacio: Mapped["Espacio"] = relationship("Calle", back_populates="ocupaciones")

    @property
    def fin_previsto(self) -> datetime:
        from datetime import timedelta
        return self.inicio_reserva + timedelta(hours=self.duracion_prevista_hs)