# conecta todas la piezas
from fastapi import FastAPI
from app.routers import estimations

app = FastAPI (
    title = "Estimador CAG",
    description = "Ssitema de estimacion de Software con arquitectura CAG",
    version = "0.1.0"
)

app.include_router(estimations.router)

@app.get("/health")
async def health():
    return {"status": "healthy"}