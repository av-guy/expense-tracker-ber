from typing import Optional
from datetime import datetime

from sqlalchemy import String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .database import BASE


class Expense(BASE):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    description: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String(200))

    def __repr__(self) -> str:
        return (
            f"Expense(id={self.id!r}, description={self.description!r},"
            f"category={self.category!r}, amount={self.amount!r}, date={self.date!r})"
        )
