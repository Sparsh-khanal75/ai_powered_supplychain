from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.database import engine

Base = declarative_base()


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ---------------------------
# User / MSME account table
# ---------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    address = Column(String)
    gst_number = Column(String)
    industry = Column(String)

    products = relationship("Product", back_populates="owner")


# ---------------------------
# Inventory / Products table
# ---------------------------

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    quantity = Column(Integer, default=0)
    price = Column(Float, default=0.0)



class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    sku = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)
    stock = Column(Integer, default=0)
    reorder_point = Column(Integer, default=0)
    unit_price = Column(Float, default=0.0)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="products")


# ---------------------------
# Supplier table
# ---------------------------
class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    product = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    delivery_time = Column(String)  # e.g., "3-5 days"
    trust_score = Column(Float, default=0.0)

    # Risk / monitoring fields (new)
    late_deliveries = Column(Integer, default=0)   # number of late deliveries
    red_flags = Column(Integer, default=0)         # manual red-flag count
    risk_score = Column(Float, default=0.0)        # computed numeric score
    risk_level = Column(String, default="Unknown") # Low / Medium / High


# ---------------------------
# Forecast / Demand table
# ---------------------------
class Forecast(Base):
    __tablename__ = "forecast"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    month = Column(String)  # e.g., "Jan", "Feb"
    actual_sales = Column(Integer, default=0)
    predicted_sales = Column(Integer, default=0)

    product = relationship("Product")
