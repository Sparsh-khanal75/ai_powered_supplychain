from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

# ---------------------------
# User / MSME account
# ---------------------------
class UserBase(BaseModel):
    business_name: str
    email: str
    phone: str
    address: Optional[str] = None
    gst_number: Optional[str] = None
    industry: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True


# ---------------------------
# Product / Inventory
# ---------------------------
class ProductBase(BaseModel):
    name: str
    sku: str
    category: str
    stock: int = 0
    reorder_point: int = 0
    unit_price: float = 0.0

class ProductCreate(ProductBase):
    owner_id: int  # link to User

class ProductUpdate(BaseModel):
    name: Optional[str]
    sku: Optional[str]
    category: Optional[str]
    stock: Optional[int]
    reorder_point: Optional[int]
    unit_price: Optional[float]

class ProductOut(ProductBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


# ---------------------------
# Supplier
# ---------------------------
class SupplierBase(BaseModel):
    name: str
    product: str
    price: float
    delivery_time: str
    trust_score: float
    late_deliveries: int = 0
    red_flags: int = 0

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    price: Optional[float]
    delivery_time: Optional[str]
    trust_score: Optional[float]
    late_deliveries: Optional[int]
    red_flags: Optional[int]

class SupplierOut(SupplierBase):
    id: int
    risk_score: float = 0
    risk_level: str = "Low"

    class Config:
        orm_mode = True

# ---------------------------
# Supplier Risk / Fraud
# ---------------------------

# ---------------------------
# Forecast / Demand
# ---------------------------
class ForecastBase(BaseModel):
    product_id: int
    month: str
    actual_sales: int = 0
    predicted_sales: int = 0

class ForecastCreate(ForecastBase):
    pass

class ForecastUpdate(BaseModel):
    actual_sales: Optional[int]
    predicted_sales: Optional[int]

class ForecastOut(ForecastBase):
    id: int

    class Config:
        orm_mode = True


class ProcurementBase(BaseModel):
    product_id: int
    supplier_id: Optional[int]
    quantity: int
    price: Optional[float] = None

class ProcurementCreate(ProcurementBase):
    pass

class ProcurementUpdate(BaseModel):
    quantity: Optional[int]
    price: Optional[float]

class ProcurementOut(ProcurementBase):
    id: int
    status: str
    requested_at: Optional[datetime]
    approved_at: Optional[datetime]

    class Config:
        orm_mode = True


class SaleBase(BaseModel):
    product_id: int
    quantity: int
    sale_date: date
    total_amount: float

class SaleCreate(SaleBase):
    pass

class SaleUpdate(BaseModel):
    quantity: Optional[int]
    sale_date: Optional[date]
    total_amount: Optional[float]

class SaleOut(SaleBase):
    id: int

    class Config:
        orm_mode = True
        

from pydantic import BaseModel
from typing import List

class SupplierRiskSummary(BaseModel):
    name: str
    risk_score: float
    risk_level: str

    class Config:
        orm_mode = True

class TopSupplier(BaseModel):
    name: str
    score: float

    class Config:
        orm_mode = True

class DashboardSummary(BaseModel):
    top_risk_suppliers: List[SupplierRiskSummary]
    top_trusted_suppliers: List[TopSupplier]
    risk_level_counts: dict  # {"Low": int, "Medium": int, "High": int}
