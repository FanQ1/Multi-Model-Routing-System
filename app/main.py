# app/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.v1.api import api_router

app = FastAPI(title="My Awesome Project")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 包含API路由
app.include_router(api_router, prefix="/api/v1")

# 根路径重定向到index.html
@app.get("/", tags=["Root"])
async def read_root():
    return FileResponse("app/static/index.html")

@app.get("/api", tags=["API"])
async def read_api():
    return {"message": "Welcome to the Awesome API!"}
