import os
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, ForeignKey, Integer, DateTime
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

engine = create_async_engine(url=os.getenv("SQL_URL"))
async_session = async_sessionmaker(engine)


class Base(DeclarativeBase):
    pass


class Type(Base):
    __tablename__ = "types"
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(20))
    ru_name: Mapped[str] = mapped_column(String(100))


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    info: Mapped[str] = mapped_column(String(500))
    photo: Mapped[str] = mapped_column(String(100))
    price: Mapped[int] = mapped_column(Integer)
    type_id: Mapped[int] = mapped_column(ForeignKey("types.id"))


class Cart(Base):
    __tablename__ = "carts"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    product_id: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(100), default="new")


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(100), default="Новый")
    price: Mapped[int] = mapped_column(Integer)
    crated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    client_name: Mapped[str] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(String(150))
    pay: Mapped[str] = mapped_column(String(100))
    phone_number: Mapped[str] = mapped_column(String(50))

class OrderCart(Base):
    __tablename__ = "ordercart"
    id: Mapped[int] = mapped_column(primary_key=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))


class Appeal(Base):
    __tablename__ = "appeals"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(String(100))
    phone_number: Mapped[str] = mapped_column(String(100))
    question: Mapped[str] = mapped_column(String(1000))
    status: Mapped[str] = mapped_column(String(100))


class User(Base):
    __tablename__ = "users"
    tg_id: Mapped[int] = mapped_column(primary_key=True)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)