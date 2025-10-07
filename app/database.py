from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise RuntimeError('DATABASE_URL missing in environment')

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


### FILE: app/models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.sql import func
from .database import Base
from sqlalchemy.orm import relationship

class Inventory(Base):
    __tablename__ = 'inventory'

    product_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    category = Column(String(100), nullable=True)
    stock_quantity = Column(Integer, nullable=False, default=0)
    reorder_threshold = Column(Integer, nullable=False, default=0)
    unit_price = Column(Float, nullable=True, default=0.0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    procurements = relationship('Procurement', back_populates='product')
    sales = relationship('SalesForecast', back_populates='product')

class Supplier(Base):
    __tablename__ = 'suppliers'  # plural recommended

    supplier_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    product = Column(String(200), nullable=False)
    price = Column(Float, nullable=False, default=0.0)
    delivery_time = Column(String(50), nullable=False)
    trust_score = Column(Float, nullable=True, default=0.0)
    late_deliveries = Column(Integer, default=0)
    red_flags = Column(Integer, default=0)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(10), default="Low")

    procurements = relationship('Procurement', back_populates='supplier')

class Procurement(Base):
    __tablename__ = 'procurement'

    procurement_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('inventory.product_id', ondelete='CASCADE'))
    supplier_id = Column(Integer, ForeignKey('supplier.supplier_id', ondelete='SET NULL'))
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=True)
    status = Column(String(50), nullable=False, default='Requested')
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)

    product = relationship('Inventory', back_populates='procurements')
    supplier = relationship('Supplier', back_populates='procurements')

class SalesForecast(Base):
    __tablename__ = 'sales_forecast'

    sale_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('inventory.product_id', ondelete='CASCADE'))
    date = Column(Date, nullable=False)
    quantity_sold = Column(Integer, nullable=True)
    predicted_demand = Column(Integer, nullable=True)

    product = relationship('Inventory', back_populates='sales')

class FraudRisk(Base):
    __tablename__ = 'fraud_risk'

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey('supplier.supplier_id', ondelete='CASCADE'))
    risk_score = Column(Float, nullable=False, default=0.0)
    last_checked = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    supplier = relationship('Supplier')