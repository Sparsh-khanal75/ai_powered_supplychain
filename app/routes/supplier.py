# app/routes/supplier.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .. import models, schemas
from ..database import get_db
from sqlalchemy.future import select

router = APIRouter(tags=["Suppliers"])   # <-- no prefix here

# List
@router.get("/", response_model=List[schemas.SupplierOut])
async def list_suppliers(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Supplier))
    return q.scalars().all()

# Create
@router.post("/", response_model=schemas.SupplierOut, status_code=status.HTTP_201_CREATED)
async def create_supplier(payload: schemas.SupplierCreate, db: AsyncSession = Depends(get_db)):
    # check uniqueness by name (optional)
    q = await db.execute(select(models.Supplier).where(models.Supplier.name == payload.name))
    existing = q.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Supplier with this name already exists")

    obj = models.Supplier(
        name=payload.name,
        product=payload.product,
        price=payload.price,
        delivery_time=payload.delivery_time,
        trust_score=payload.trust_score,
        late_deliveries=payload.late_deliveries,
        red_flags=payload.red_flags
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

# Get
@router.get("/{supplier_id}", response_model=schemas.SupplierOut)
async def get_supplier(supplier_id: int, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Supplier).where(models.Supplier.id == supplier_id))
    item = q.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return item

# Update
@router.put("/{supplier_id}", response_model=schemas.SupplierOut)
async def update_supplier(supplier_id: int, payload: schemas.SupplierUpdate, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Supplier).where(models.Supplier.id == supplier_id))
    item = q.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Supplier not found")

    if payload.price is not None:
        item.price = payload.price
    if payload.delivery_time is not None:
        item.delivery_time = payload.delivery_time
    if payload.trust_score is not None:
        item.trust_score = payload.trust_score
    if payload.late_deliveries is not None:
        item.late_deliveries = payload.late_deliveries
    if payload.red_flags is not None:
        item.red_flags = payload.red_flags

    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

# Delete
@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(supplier_id: int, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Supplier).where(models.Supplier.id == supplier_id))
    item = q.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Supplier not found")
    await db.delete(item)
    await db.commit()
    return None

# Compute risk (operate in-place on Supplier model)
@router.post("/compute-risks")
async def compute_supplier_risks(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Supplier))
    suppliers = q.scalars().all()

    for supplier in suppliers:
        # simple formula (tune as needed)
        score = (supplier.late_deliveries * 2) + (supplier.red_flags * 5) + max(0, 10 - (supplier.trust_score or 0))
        supplier.risk_score = float(score)
        if score <= 10:
            supplier.risk_level = "Low"
        elif score <= 20:
            supplier.risk_level = "Medium"
        else:
            supplier.risk_level = "High"
        db.add(supplier)

    await db.commit()
    return {"message": "Supplier risks computed successfully!"}
