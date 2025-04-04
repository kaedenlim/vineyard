from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional

class OnboardDTO(BaseModel):
    shopee_url: Optional[HttpUrl] = None  
    lazada_url: Optional[HttpUrl] = None
    carousell_url: Optional[HttpUrl] = None

    @field_validator("shopee_url", "lazada_url", "carousell_url", mode="before")
    @classmethod
    def empty_str_to_none(cls, value):
        if value == "":
            return None
        return value

class ScrapeDTO(BaseModel):
    product: str