from pydantic import BaseModel, HttpUrl
from typing import Optional

class OnboardDTO(BaseModel):
    username: str 
    shopee_url: Optional[HttpUrl] = ""  
    lazada_url: Optional[HttpUrl] = ""
    carousell_url: Optional[HttpUrl] = ""

class ScrapeDTO(BaseModel):
    username: str 
    product: str

class DashboardDTO(BaseModel):
    username: str