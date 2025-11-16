import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger, String, Text, Boolean, Numeric, DateTime, Enum, Date,
    ForeignKey, UniqueConstraint, Index, text
)
    
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base

class Gender(enum.Enum):
    # Значения enum — то, что реально сохранится в БД.
    male = "male"
    female = "female"


class PaymentProvider(enum.Enum):
    # Идентификатор провайдера оплаты — нужен для идеempotентности и сверок.
    prodamus = "prodamus"
    robokassa = "robokassa"
    manual = "manual"  # на всякий случай: ручные платежи/корректировки


class OrderStatus(enum.Enum):
    # Жизненный цикл платежа/заказа.
    pending = "pending"     # создан, ждём оплату/вебхук
    paid = "paid"           # оплачен (получили подтверждающий вебхук)
    failed = "failed"       # ошибка/отмена
    refunded = "refunded"   # возврат оформлен


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, index=True, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(32), nullable=True)
    email: Mapped[str | None] = mapped_column(CITEXT, unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(255))
    lang: Mapped[str] = mapped_column(String(8), default="ru", nullable=False)

    birth_date: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[Gender | None] = mapped_column(Enum(Gender, name="gender_enum"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    is_subscribed: Mapped[bool] = mapped_column(Boolean, server_default=text("true"), nullable=False)
    unsubscribed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    #purchases - Связь с покупками:
        #  - cascade удалит покупки при удалении пользователя,
        #  - selectin — эффективная подгрузка коллекции без постоянных JOIN’ов.
    purchases: Mapped[list["Purchase"]] = relationship(
        back_populates="user", cascade="all,delete-orphan", lazy="selectin"
    )


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    #code - стабильный "slug" товара для логики (не человекочитаемый title).
        # Удобно использовать в коде/кнопках/настройках.
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    
    #price - Базовая цена товара "сейчас".
    # Важно: это НЕ цена конкретной покупки c учетом скидок или промокодов — та фиксируется в Purchase.
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), server_default="RUB", nullable=False)  # ISO-4217
    
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    purchases: Mapped[list["Purchase"]] = relationship(back_populates="product", cascade="all,delete-orphan", lazy="selectin")


class Purchase(Base):
    __tablename__ = "purchases"
    __table_args__ = (
        # один и тот же платёж (по провайдеру и внешнему id заказа) не запишется дважды.
        UniqueConstraint("provider", "external_order_id", name="uq_provider_ext_order"),
        Index("ix_purchases_user_created_at", "user_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    
    # Цена сделки: СКОЛЬКО реально заплатили в момент покупки.
    # Не равна обязательно Product.price (бывают скидки/акции/изменения каталога).
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), server_default="RUB", nullable=False)

    provider: Mapped[PaymentProvider] = mapped_column(Enum(PaymentProvider, name="payment_provider_enum"), nullable=False)
    
    #external_order_id - Идентификатор заказа/инвойса у внешнего провайдера (например, Prodamus).
    #Используется для сверки, рефандов, повторных вебхуков и идеempotентности
    external_order_id: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status_enum"),
        default=OrderStatus.pending,  # python default
        server_default=text("'pending'::order_status_enum"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="purchases", lazy="selectin")
    product: Mapped["Product"] = relationship(back_populates="purchases", lazy="selectin")
