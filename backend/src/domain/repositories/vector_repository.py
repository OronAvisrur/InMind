from typing import Protocol, List, Optional
from src.domain.models.product import Product
from src.domain.models.search_result import SearchResult

class VectorRepository(Protocol):
    async def add_products(self, products: List[Product]) -> None:
        ...
    
    async def search(
        self, 
        query_embedding: List[float], 
        top_k: int = 5,
        filters: Optional[dict] = None
    ) -> List[SearchResult]:
        ...
    
    async def delete_product(self, product_id: str) -> None:
        ...
    
    async def get_product_count(self) -> int:
        ...