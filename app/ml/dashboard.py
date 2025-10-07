from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .. import models, schemas
from ..database import get_db
from collections import Counter

router = APIRouter(
    prefix="/api/ml/dashboard",
    tags=["Dashboard"]
)

@router.get("/", response_model=schemas.DashboardSummary)
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):

    # Fetch suppliers
    q = await db.execute(select(models.Supplier))
    suppliers = q.scalars().all()

    # Top 5 risk suppliers
    top_risk_suppliers = sorted(suppliers, key=lambda s: s.risk_score, reverse=True)[:5]

    # Top 5 trusted suppliers
    top_trusted_suppliers = sorted(suppliers, key=lambda s: s.trust_score, reverse=True)[:5]

    # Risk level counts
    risk_counts = Counter([s.risk_level for s in suppliers])

    return schemas.DashboardSummary(
        top_risk_suppliers=top_risk_suppliers,
        top_trusted_suppliers=[{"name": s.name, "score": s.trust_score} for s in top_trusted_suppliers],
        risk_level_counts=dict(risk_counts)
    )
