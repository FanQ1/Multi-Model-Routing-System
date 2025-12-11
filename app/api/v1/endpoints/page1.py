
from fastapi import APIRouter
from app.schemas.page1 import Page1Request, Page1Response
from app.services.page1_service import process_page1_data

router = APIRouter()

@router.get("/", response_model=Page1Response)
async def get_page1_data():
    """
    获取页面1的初始数据
    """
    return {"message": "这是页面1的初始数据", "data": {}}

@router.post("/", response_model=Page1Response)
async def handle_page1_request(request: Page1Request):
    """
    处理页面1的请求
    """
    result = process_page1_data(request.data)
    return {"message": "页面1请求处理成功", "data": result}
