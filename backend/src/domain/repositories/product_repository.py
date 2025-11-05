from typing import Protocol, List, Optional, Dict, Any
from ..models import Product
from ..value_objects import ProductIdentifier, PriceRange


class ProductRepository(Protocol):
    async def create(self, product: Product) -> Product:
        ...

    async def get_by_id(self, product_id: ProductIdentifier) -> Optional[Product]:
        ...

    async def find_by_category(self, category: str, limit: int = 20) -> List[Product]:
        ...

    async def find_by_brand(self, brand: str, limit: int = 20) -> List[Product]:
        ...

    async def find_by_price_range(self, price_range: PriceRange, limit: int = 20) -> List[Product]:
        ...

    async def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20
    ) -> List[Product]:
        ...

    async def find_similar(self, product_id: ProductIdentifier, limit: int = 10) -> List[Product]:
        ...

    async def update(self, product: Product) -> Product:
        ...

    async def delete(self, product_id: ProductIdentifier) -> bool:
        ...

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        ...