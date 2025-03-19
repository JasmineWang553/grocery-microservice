from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="Grocery List API", description="FastAPI MongoDB Example", version="1.0.0")

app.include_router(router)