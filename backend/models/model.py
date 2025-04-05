from dataclasses import dataclass
from typing import List

@dataclass
class Product:
    title: str
    price: float
    discount: float
    image: str
    link: str
    page_ranking: int

@dataclass
class ScrapeResult:
    scraped_data: List[Product]
    timestamp: str
    average_price: float
    top_listings: List[Product]

@dataclass
class InsightsData:
    product_name: str
    carousell_average_price: float
    carousell_top_listings: List[Product]