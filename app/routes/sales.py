from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .. import models, schemas
from ..database import get_db
from sqlalchemy.future import select

router = APIRouter(
    prefix="/api/sales",
    tags=["Sales"]
)

# List all sales
@router.get("/", response_model=List[schemas.SaleOut])
async def list_sales(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Sale))
    items = q.scalars().all()
    return items

# Create a sale
@router.post("/", response_model=schemas.SaleOut, status_code=status.HTTP_201_CREATED)
async def create_sale(payload: schemas.SaleCreate, db: AsyncSession = Depends(get_db)):
    obj = models.Sale(
        product_id=payload.product_id,
        quantity=payload.quantity,
        sale_date=payload.sale_date,
        total_amount=payload.total_amount
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

# Get sale by ID
@router.get("/{sale_id}", response_model=schemas.SaleOut)
async def get_sale(sale_id: int, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Sale).where(models.Sale.id == sale_id))
    item = q.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Sale not found")
    return item

# Update sale
@router.put("/{sale_id}", response_model=schemas.SaleOut)
async def update_sale(sale_id: int, payload: schemas.SaleUpdate, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Sale).where(models.Sale.id == sale_id))
    item = q.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Sale not found")

    if payload.quantity is not None:
        item.quantity = payload.quantity
    if payload.sale_date is not None:
        item.sale_date = payload.sale_date
    if payload.total_amount is not None:
        item.total_amount = payload.total_amount

    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

# Delete sale
@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sale(sale_id: int, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Sale).where(models.Sale.id == sale_id))
    item = q.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    await db.delete(item)
    await db.commit()
    return None
