import enum
from datetime import date, datetime, time

from sqlalchemy import (
    BigInteger, String, Text, Boolean, DateTime, Enum, Date, Time, Float, Integer,
    ForeignKey, CheckConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base


class UserStatus(enum.Enum):
    FREE = "free"
    PREMIUM = "premium"


class Gender(enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    UNKNOWN = "UNKNOWN"


class ContentType(enum.Enum):
    TEXT = "TEXT"
    FILE = "FILE"


class MailingStatus(enum.Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"


class MediaType(enum.Enum):
    PHOTO = "PHOTO"
    VIDEO = "VIDEO"
    ANIMATION = "ANIMATION"
    DOCUMENT = "DOCUMENT"
    NONE = "NONE"


class MailingLogStatus(enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class PaymentProvider(enum.Enum):
    PRODAMUS = "prodamus"
    ROBOKASSA = "robokassa"
    MANUAL = "manual"


class User(Base):
    __tablename__ = "users"
    
    # Primary (Automated)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(32), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_tele_prem: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus, name="user_status_enum"), default=UserStatus.FREE, nullable=False)
    reg_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_visit_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    referred_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    language_code: Mapped[str] = mapped_column(String(8), server_default="ru", nullable=False)

    # Secondary (Manual Input)
    fio: Mapped[str | None] = mapped_column(String(255))
    gender: Mapped[Gender | None] = mapped_column(Enum(Gender, name="gender_enum"))
    birth_city: Mapped[str | None] = mapped_column(String(128))
    birthday: Mapped[date | None] = mapped_column(Date)
    birth_time: Mapped[time | None] = mapped_column(Time)
    birth_lat: Mapped[float | None] = mapped_column(Float)
    birth_lon: Mapped[float | None] = mapped_column(Float)
    timezone: Mapped[str | None] = mapped_column(String(64))
    zodiac_sign: Mapped[str | None] = mapped_column(String(32))

    # Relationships
    purchases: Mapped[list["Purchase"]] = relationship(back_populates="user", cascade="all,delete-orphan", lazy="selectin")
    mailing_logs: Mapped[list["MailingLog"]] = relationship(back_populates="user", cascade="all,delete-orphan", lazy="select")
    promocodes: Mapped[list["PromoCode"]] = relationship(back_populates="allowed_user", cascade="all,delete-orphan", lazy="select")


class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    content_type: Mapped[ContentType] = mapped_column(Enum(ContentType, name="content_type_enum"), nullable=False)
    content_data: Mapped[str | None] = mapped_column(Text)

    purchases: Mapped[list["Purchase"]] = relationship(back_populates="product", cascade="all,delete-orphan", lazy="selectin")


class Purchase(Base):
    __tablename__ = "purchases"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    purchase_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    user: Mapped["User"] = relationship(back_populates="purchases", lazy="selectin")
    product: Mapped["Product"] = relationship(back_populates="purchases", lazy="selectin")


class PromoCode(Base):
    __tablename__ = "promocodes"
    
    code: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    discount_percent: Mapped[int] = mapped_column(Integer, CheckConstraint('discount_percent >= 1 AND discount_percent <= 100', name='chk_discount_pct'), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    max_uses: Mapped[int | None] = mapped_column(Integer)
    current_uses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    allowed_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    target_product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))

    allowed_user: Mapped["User"] = relationship(back_populates="promocodes")


class MailingCampaign(Base):
    __tablename__ = "mailing_campaigns"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    text_content: Mapped[str | None] = mapped_column(Text)
    status: Mapped[MailingStatus] = mapped_column(Enum(MailingStatus, name="mailing_status_enum"), default=MailingStatus.DRAFT, nullable=False)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    media_type: Mapped[MediaType] = mapped_column(Enum(MediaType, name="media_type_enum"), default=MediaType.NONE, nullable=False)
    media_file_id: Mapped[str | None] = mapped_column(String(255))
    reply_markup: Mapped[dict | list | None] = mapped_column(JSONB)
    
    logs: Mapped[list["MailingLog"]] = relationship(back_populates="campaign", cascade="all,delete-orphan", lazy="select")


class MailingLog(Base):
    __tablename__ = "mailing_logs"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("mailing_campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[MailingLogStatus] = mapped_column(Enum(MailingLogStatus, name="mailing_log_status_enum"), default=MailingLogStatus.PENDING, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="mailing_logs")
    campaign: Mapped["MailingCampaign"] = relationship(back_populates="logs")
