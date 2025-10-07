from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from .database import engine, Base
from .routes import inventory , users , supplier,procurement,sales,forecast,analytics

app = FastAPI(title='MCP Server — MSME Supply Chain Optimizer')
from .ml import dashboard

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers


app.include_router(dashboard.router)

app.include_router(inventory.router, prefix="/api/inventory", tags=["inventory"]) 
app.include_router(users.router, prefix="/api/users") 
app.include_router(supplier.router,prefix="/api/suppliers")

app.include_router(procurement.router, prefix="/api/procurement", tags=["procurement"])
app.include_router(sales.router, prefix="/api/sales", tags=["Sales"])
app.include_router(forecast.router, prefix="/api/forecast", tags=["Forecast"])
app.include_router(analytics.router)


# Startup event to create tables (for development only)
@app.on_event("startup")
async def on_startup():

    # Create DB tables if they don't exist (development convenience)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)