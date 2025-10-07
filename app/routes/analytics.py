from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .. import models
from ..database import get_db

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"]
)

# Total products count
@router.get("/inventory/total")
async def total_products(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Product))
    products = q.scalars().all()
    return {"total_products": len(products)}

# Low stock products (stock <= reorder_point)
@router.get("/inventory/low-stock")
async def low_stock_products(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Product))
    products = q.scalars().all()
    low_stock = [p.name for p in products if p.stock <= p.reorder_point and p.stock > 0]
    return {"low_stock_products": low_stock, "count": len(low_stock)}

# Critical stock products (stock == 0)
@router.get("/inventory/critical")
async def critical_stock_products(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Product))
    products = q.scalars().all()
    critical = [p.name for p in products if p.stock == 0]
    return {"critical_stock_products": critical, "count": len(critical)}

# Total inventory value
@router.get("/inventory/total-value")
async def total_inventory_value(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Product))
    products = q.scalars().all()
    total_value = sum(p.stock * p.unit_price for p in products)
    return {"total_inventory_value": total_value}

@router.get("/inventory/alerts")
async def inventory_alerts(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Product))
    products = q.scalars().all()
    
    low_stock = [p.name for p in products if 0 < p.stock <= p.reorder_point]
    critical_stock = [p.name for p in products if p.stock == 0]

    return {
        "low_stock_products": low_stock,
        "low_stock_count": len(low_stock),
        "critical_stock_products": critical_stock,
        "critical_stock_count": len(critical_stock)
    }

@router.get("/suppliers/alerts")
async def supplier_risk_alerts(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.SupplierRisk))
    risks = q.scalars().all()
    
    high_risk = [r.supplier_id for r in risks if r.risk_level.lower() == "high"]
    medium_risk = [r.supplier_id for r in risks if r.risk_level.lower() == "medium"]
    
    return {
        "high_risk_suppliers": high_risk,
        "high_risk_count": len(high_risk),
        "medium_risk_suppliers": medium_risk,
        "medium_risk_count": len(medium_risk)
    }

@router.get("/sales/total")
async def total_sales(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Sale))
    sales = q.scalars().all()
    total = sum(s.quantity * s.unit_price for s in sales)
    return {"total_sales_value": total}

# -------------------------------
# Sales by product
# -------------------------------
@router.get("/sales/by-product")
async def sales_by_product(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Sale))
    sales = q.scalars().all()
    result = {}
    for s in sales:
        if s.product_id not in result:
            result[s.product_id] = 0
        result[s.product_id] += s.quantity * s.unit_price
    return {"sales_by_product": result}

# -------------------------------
# Monthly sales trend
# -------------------------------
@router.get("/sales/monthly")
async def monthly_sales(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Sale))
    sales = q.scalars().all()
    result = {}
    for s in sales:
        month = s.date.strftime("%Y-%m")  # assuming Sale has `date` field
        if month not in result:
            result[month] = 0
        result[month] += s.quantity * s.unit_price
    return {"monthly_sales": result}



# -------------------------------
# Forecast vs Actual Comparison
# -------------------------------
@router.get("/forecast/accuracy")
async def forecast_accuracy(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Forecast))
    forecasts = q.scalars().all()
    result = []
    for f in forecasts:
        accuracy = 0
        if f.predicted_sales:
            accuracy = round((f.actual_sales / f.predicted_sales) * 100, 2)
        result.append({
            "product_id": f.product_id,
            "month": f.month,
            "actual_sales": f.actual_sales,
            "predicted_sales": f.predicted_sales,
            "accuracy_percent": accuracy
        })
    return {"forecast_accuracy": result}
