from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from .. import models, schemas
from ..database import get_db
from sqlalchemy.future import select
from datetime import datetime

router = APIRouter(
    prefix="/api/procurement",
    tags=["Procurement"]
)

# List all procurement records
@router.get("/", response_model=List[schemas.ProcurementOut])
async def list_procurements(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Procurement).offset(skip).limit(limit))
    items = q.scalars().all()
    return items

# Create a procurement request
@router.post("/", response_model=schemas.ProcurementOut, status_code=status.HTTP_201_CREATED)
async def create_procurement(payload: schemas.ProcurementCreate, db: AsyncSession = Depends(get_db)):
    # Optional: validate product exists
    q = await db.execute(select(models.Product).where(models.Product.id == payload.product_id))
    product = q.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    obj = models.Procurement(
        product_id=payload.product_id,
        supplier_id=payload.supplier_id,
        quantity=payload.quantity,
        price=payload.price,
        status="requested",
        requested_at=datetime.utcnow()
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

# Get procurement by ID
@router.get("/{procurement_id}", response_model=schemas.ProcurementOut)
async def get_procurement(procurement_id: int, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Procurement).where(models.Procurement.procurement_id == procurement_id))
    item = q.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Procurement record not found")
    return item

# Update procurement (quantity, price, supplier, or status)
@router.put("/{procurement_id}", response_model=schemas.ProcurementOut)
async def update_procurement(procurement_id: int, payload: schemas.ProcurementBase, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Procurement).where(models.Procurement.procurement_id == procurement_id))
    item = q.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Procurement record not found")

    if payload.quantity is not None:
        item.quantity = payload.quantity
    if payload.price is not None:
        item.price = payload.price
    if payload.supplier_id is not None:
        item.supplier_id = payload.supplier_id

    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

# Delete procurement
@router.delete("/{procurement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_procurement(procurement_id: int, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Procurement).where(models.Procurement.procurement_id == procurement_id))
    item = q.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Procurement record not found")
    
    await db.delete(item)
    await db.commit()
    return None
