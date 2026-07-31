from fastapi import FastAPI
from routes import router as gateway_router

app = FastAPI(
    title="Bezalel Foundry Gateway",
    description="Standalone gateway service for Bezalel Foundry",
    version="1.0.0"
)

app.include_router(gateway_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
