from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app import db


class Product(db.Model):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    def __repr__(self):
        return f"<Product {self.id} {self.name!r} {self.price}>"
