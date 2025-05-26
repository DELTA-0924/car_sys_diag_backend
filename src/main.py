from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
from src.db.dbConnect import init_db
from src.api.routes.auth_routes import auth_router
from fastapi.staticfiles import StaticFiles
from src.api.routes.car_routes import car_router
from src.api.routes.sensor_routes import sensor_router
from .errors import register_all_errors
from .middleware import register_middleware

import os
import subprocess


redis_path = "D:\\programs\\redis\\redis-server.exe"




@asynccontextmanager
async def life_span(app: FastAPI):
    print(f"server is starting...")
    if not os.path.exists(redis_path):
        print(f"❌ Файл не найден: {redis_path}")
    else:
        try:
            print("🚀 Запуск Redis-сервера...")
            subprocess.Popen(redis_path)
            print("✅ Redis запущен.")
        except Exception as e:
            print(f"⚠️ Ошибка запуска: {e}")
    await init_db()
    yield
    print(f"server has been stopped")


version = "v1"
app = FastAPI(    
    title="Product",
    description=" A REST API for  a book  review  web service ",
    version=version,
    lifespan=life_span
)


register_all_errors(app)
register_middleware(app)

app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])

app.include_router(car_router, prefix=f"/api/{version}/car", tags=["car"])
app.include_router(sensor_router, prefix=f"/api/{version}/sensor", tags=["sensors"])
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=False)