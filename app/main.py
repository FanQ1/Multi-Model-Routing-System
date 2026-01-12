# app/main.py

from fastapi import FastAPI
from app.api.v1.api import api_router

app = FastAPI(title="router")

app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Awesome API!"}
