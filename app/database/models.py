from sqlalchemy import Column, Integer, BigInteger, String, Enum, DateTime, Boolean, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from datetime import datetime, date


engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3', echo=True)
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass


class Driver(Base):
    __tablename__ = 'drivers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # Уникальный идентификатор водителя
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)  # Telegram ID водителя
    last_name = Column(String, nullable=False)  # Фамилия
    first_name = Column(String, nullable=False)  # Имя
    middle_name = Column(String, nullable=True)  # Отчество
    full_name: Mapped[str] = mapped_column(String, nullable=False)  # ФИО
    phone: Mapped[str] = mapped_column(String, unique=True, nullable=False)  # Рабочий телефон
    city: Mapped[str] = mapped_column(String, nullable=False)  # Город проживания
    car_make: Mapped[str] = mapped_column(String, nullable=False)  # Марка автомобиля
    car_plate: Mapped[str] = mapped_column(String, unique=True, nullable=False)  # Гос. номер автомобиля
    license_number: Mapped[str] = mapped_column(String, nullable=False)  # URL номера водительских прав
    license_front_url: Mapped[str] = mapped_column(String, nullable=False)  # URL фото лицевой стороны прав
    license_back_url: Mapped[str] = mapped_column(String, nullable=False)  # URL фото обратной стороны прав
    car_photo_1: Mapped[str] = mapped_column(String, nullable=False)  # Фото автомобиля (вид 1)
    car_photo_2: Mapped[str] = mapped_column(String, nullable=False)  # Фото автомобиля (вид 2)
    car_photo_3: Mapped[str] = mapped_column(String, nullable=False)  # Фото автомобиля (вид 3)
    selfie_with_car: Mapped[str] = mapped_column(String, nullable=False)  # Фото водитель + авто
    registration_date: Mapped[date] = mapped_column(Date, default=date.today)  # Дата регистрации
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)  # Статус блокировки
    comments: Mapped[str] = mapped_column(String, nullable=True)  # Комментарии
    verification: Mapped[bool] = mapped_column(Boolean, default=False)


'''class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer, unique=True, nullable=False)  # Telegram ID администратора
    full_name = Column(String, nullable=False)  # ФИО администратора

class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=False)  # ID водителя
    admin_id = Column(Integer, ForeignKey('admins.id'), nullable=True)  # ID администратора
    message = Column(String, nullable=False)  # Сообщение
    created_at = Column(Date, default=date.today)  # Дата создания

    driver = relationship('Driver', back_populates='notifications')
    admin = relationship('Admin', back_populates='notifications')

Driver.notifications = relationship('Notification', back_populates='driver', cascade='all, delete-orphan')
Admin.notifications = relationship('Notification', back_populates='admin', cascade='all, delete-orphan')'''


# Асинхронное создание таблиц
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)