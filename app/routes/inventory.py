from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from datetime import datetime

from .. import models, schemas
from ..database import get_db

router = APIRouter()


# ---------------------------
# CRUD: Products
# ---------------------------

@router.get("/products", response_model=List[schemas.ProductOut])
async def list_products(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Product).offset(skip).limit(limit))
    items = q.scalars().all()
    return items


@router.post("/products", response_model=schemas.ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(payload: schemas.ProductCreate, db: AsyncSession = Depends(get_db)):
    # Check unique name
    q = await db.execute(select(models.User).where(models.User.id == payload.owner_id))
    owner = q.scalar_one_or_none()
    if not owner:
        raise HTTPException(status_code=400, detail="Invalid owner_id, user does not exist")

    obj = models.Product(
        name=payload.name,
        sku=payload.sku,
        category=payload.category,
        stock=payload.stock,
        reorder_point=payload.reorder_point,
        unit_price=payload.unit_price,
        owner_id=payload.owner_id
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.get("/products/{product_id}", response_model=schemas.ProductOut)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Product).where(models.Product.id == product_id))
    item = q.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Product not found")
    return item


@router.put("/products/{product_id}", response_model=schemas.ProductOut)
async def update_product(product_id: int, payload: schemas.ProductUpdate, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Product).where(models.Product.id == product_id))
    item = q.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update fields if provided
    if payload.name is not None:
        item.name = payload.name
    if payload.sku is not None:
        item.sku = payload.sku
    if payload.category is not None:
        item.category = payload.category
    if payload.stock is not None:
        item.stock = payload.stock
    if payload.reorder_point is not None:
        item.reorder_point = payload.reorder_point
    if payload.unit_price is not None:
        item.unit_price = payload.unit_price

    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Product).where(models.Product.id == product_id))
    item = q.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.delete(item)
    await db.commit()
    return None


# ---------------------------
# Stats / Alerts
# ---------------------------

@router.get("/stats/total")
async def total_products(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Product))
    total = len(q.scalars().all())
    return {"total": total}


@router.get("/stats/low-stock")
async def low_stock_count(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Product))
    items = q.scalars().all()
    low = [i for i in items if i.stock <= i.reorder_point and i.stock > 0]
    return {"low_stock_count": len(low)}


@router.get("/stats/critical")
async def critical_stock_count(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Product))
    items = q.scalars().all()
    critical = [i for i in items if i.stock == 0 or i.stock < (i.reorder_point // 2)]
    return {"critical_stock_count": len(critical)}


@router.get("/stats/total-value")
async def total_value(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Product))
    items = q.scalars().all()
    total_value = sum((i.unit_price or 0.0) * (i.stock or 0) for i in items)
    return {"total_value": round(total_value, 2)}


@router.get("/alerts")
async def stock_alerts(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Product))
    items = q.scalars().all()
    alerts = []
    for i in items:
        if i.stock <= 0:
            alerts.append({
                "type": "destructive",
                "title": f"{i.name} out of stock",
                "description": f"{i.name} has zero stock"
            })
        elif i.stock <= i.reorder_point:
            alerts.append({
                "type": "warning",
                "title": f"Low stock: {i.name}",
                "description": f"{i.name} at {i.stock} units (threshold {i.reorder_point})"
            })
    return {"alerts": alerts}
