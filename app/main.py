from fastapi import FastAPI
from app.api.v1 import router as v1_router
from app.infra.database import engine, Base
from loguru import logger

# Initialize Database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="YouTube Intelligence Suite",
    description="Professional YouTube Channel Analytics & Strategic Insights",
    version="3.0.0"
)

# Register Routers
app.include_router(v1_router, prefix="/api/v1", tags=["v1"])

@app.get("/")
async def root():
    return {
        "status": "online",
        "version": "3.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
