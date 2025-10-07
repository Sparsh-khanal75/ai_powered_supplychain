# app/routes/forecast.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from .. import models, schemas
from ..database import get_db

# ML imports
from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd

router = APIRouter(  # no prefix here
    tags=["Forecast"]
)

# Predict route — keep this BEFORE the dynamic /{forecast_id} route
@router.get("/predict")
async def forecast_predict(
    db: AsyncSession = Depends(get_db),
    forecast_id: Optional[int] = Query(None, description="Optional forecast ID to filter")
):
    """
    Predict next 3 months of sales using simple Linear Regression.
    If forecast_id is provided, use data only for that forecast.
    """
    # Query data (use forecast_id as a filter if provided)
    if forecast_id is not None:
        q = await db.execute(select(models.Forecast).where(models.Forecast.id == forecast_id))
    else:
        q = await db.execute(select(models.Forecast))
    data = q.scalars().all()

    if not data:
        return {"message": "No historical data available for forecasting."}

    # Build DataFrame and sort by month
    df = pd.DataFrame([{"month": f.month, "actual_sales": f.actual_sales} for f in data])
    df = df.sort_values("month")

    # Encode months as simple numeric sequence and fit model
    X = np.arange(len(df)).reshape(-1, 1)
    y = df["actual_sales"].values

    model = LinearRegression()
    model.fit(X, y)

    # Predict next 3 months
    next_months = np.arange(len(df), len(df) + 3).reshape(-1, 1)
    preds = model.predict(next_months)

    forecast_result = [
        {"month": f"Month {len(df) + i}", "predicted_sales": round(float(pred), 2)}
        for i, pred in enumerate(preds, 1)
    ]

    return {"historical_points": len(df), "forecast_for_next_months": forecast_result}


# --- Standard CRUD endpoints (static paths below predict) ---

@router.get("/", response_model=List[schemas.ForecastOut])
async def list_forecasts(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Forecast))
    return q.scalars().all()

@router.post("/", response_model=schemas.ForecastOut, status_code=status.HTTP_201_CREATED)
async def create_forecast(payload: schemas.ForecastCreate, db: AsyncSession = Depends(get_db)):
    obj = models.Forecast(
        product_id=payload.product_id,
        month=payload.month,
        actual_sales=payload.actual_sales,
        predicted_sales=payload.predicted_sales
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

@router.get("/{forecast_id}", response_model=schemas.ForecastOut)
async def get_forecast(forecast_id: int, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Forecast).where(models.Forecast.id == forecast_id))
    item = q.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Forecast not found")
    return item

@router.put("/{forecast_id}", response_model=schemas.ForecastOut)
async def update_forecast(forecast_id: int, payload: schemas.ForecastUpdate, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Forecast).where(models.Forecast.id == forecast_id))
    item = q.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Forecast not found")
    if payload.actual_sales is not None:
        item.actual_sales = payload.actual_sales
    if payload.predicted_sales is not None:
        item.predicted_sales = payload.predicted_sales
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

@router.delete("/{forecast_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_forecast(forecast_id: int, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(models.Forecast).where(models.Forecast.id == forecast_id))
    item = q.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Forecast not found")
    await db.delete(item)
    await db.commit()
    return None

@router.post("/seed")
async def seed_forecasts(db: AsyncSession = Depends(get_db)):
    sample_data = [
        models.Forecast(product_id=2, month="2025-01", actual_sales=1200.0),
        models.Forecast(product_id=2, month="2025-02", actual_sales=1350.0),
        models.Forecast(product_id=2, month="2025-03", actual_sales=1600.0),
        models.Forecast(product_id=2, month="2025-04", actual_sales=1750.0),
        models.Forecast(product_id=2, month="2025-05", actual_sales=1900.0),
    ]
    db.add_all(sample_data)
    await db.commit()
    return {"message": "Dummy forecast data added successfully!"}
# Note: In a real app, remove this endpoint or protect it properly.