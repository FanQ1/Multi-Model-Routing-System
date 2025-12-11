
from pydantic import BaseModel, Dict, Any

class Page1Request(BaseModel):
    data: Dict[str, Any] = {}

class Page1Response(BaseModel):
    message: str
    data: Dict[str, Any] = {}
