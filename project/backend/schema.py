from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field, EmailStr

class UserBase(BaseModel):
    username: str
    email: EmailStr

T = TypeVar('T')
class ApiResponse(BaseModel, Generic[T]):
    """通用API响应模型"""
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")