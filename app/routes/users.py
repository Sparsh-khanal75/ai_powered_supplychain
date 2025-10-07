from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/users", tags=["Users"])

# Create user
@router.post("/", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(payload: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if email already exists
    q = await db.execute(select(models.User).where(models.User.email == payload.email))
    existing = q.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    obj = models.User(
        business_name=payload.business_name,
        email=payload.email,
        phone=payload.phone,
        password_hash=payload.password,  # ideally hash this
        address=payload.address,
        gst_number=payload.gst_number,
        industry=payload.industry
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

# List all users
@router.get("/", response_model=List[schemas.UserOut])
async def list_users(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.User))
    users = q.scalars().all()
    return users
