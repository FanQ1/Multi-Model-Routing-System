
from fastapi import APIRouter
from app.schemas.page2 import Page2Request, Page2Response
from app.services.page2_service import process_page2_data

router = APIRouter()

@router.get("/", response_model=Page2Response)
async def get_page2_data():
    """
    获取页面2的初始数据
    """
    return {"message": "这是页面2的初始数据", "data": {}}

@router.post("/", response_model=Page2Response)
async def handle_page2_request(request: Page2Request):
    """
    处理页面2的请求
    """
    result = process_page2_data(request.data)
    return {"message": "页面2请求处理成功", "data": result}
