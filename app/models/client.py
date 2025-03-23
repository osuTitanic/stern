
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class Client(BaseModel):
    name: str
    description: str
    category: str
    known_bugs: Optional[str]
    supported: bool
    preview: bool
    downloads: List[str]
    screenshots: List[str]
    hashes: List[dict]
    created_at: datetime
