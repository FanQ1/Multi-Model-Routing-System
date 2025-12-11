
from pydantic import BaseModel, Dict, Any

class Page2Request(BaseModel):
    data: Dict[str, Any] = {}

class Page2Response(BaseModel):
    message: str
    data: Dict[str, Any] = {}
