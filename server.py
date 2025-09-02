from contextlib import asynccontextmanager
from fastapi import FastAPI
from utils.database_config import create_all_tables
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from routes.user_org import router as user_org_router
from routes.firmware import router as firmware_router
from routes.profile import router as profile_router
from routes.device import router as device_router
from routes.device_data import router as device_data_router

origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "*"
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables and default admin/org at startup
    try:
        print("Creating database tables...")
        create_all_tables()
        print("✅ Database initialization complete")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise
    yield
    # Place for any cleanup logic if needed
    print("Application shutting down...")

app = FastAPI(
    title="IoTHub FastAPI API",
    description="Backend API for IoTHub system.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_org_router, prefix="/api/v1", tags=["UserOrg"])
app.include_router(firmware_router, prefix="/api/v1", tags=["Firmware"])
app.include_router(profile_router, prefix="/api/v1", tags=["Profile"])
app.include_router(device_router, prefix="/api/v1", tags=["Device"])
app.include_router(device_data_router, prefix="/api/v1", tags=["DeviceData"])

@app.get("/")
def root():
    return {"message": "IoTHub FastAPI server is running."}

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
