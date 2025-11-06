from typing import List
from src.domain.models.product import Product
from src.domain.repositories.embedding_repository import EmbeddingRepository
from src.domain.repositories.vector_repository import VectorRepository

class ProductIngestionService:
    def __init__(
        self,
        embedding_service: EmbeddingRepository,
        vector_repository: VectorRepository
    ):
        self._embedding_service = embedding_service
        self._vector_repository = vector_repository
    
    async def ingest_products(self, products: List[Product]) -> int:
        if not products:
            return 0
        
        await self._vector_repository.add_products(products)
        return len(products)
    
    async def ingest_product(self, product: Product) -> None:
        await self._vector_repository.add_products([product])
    
    async def remove_product(self, product_id: str) -> None:
        await self._vector_repository.delete_product(product_id)
    
    async def get_total_products(self) -> int:
        return await self._vector_repository.get_product_count()
    
    async def search_products(
        self,
        query_text: str,
        top_k: int = 5,
        filters: dict = None
    ) -> List:
        query_embedding = await self._embedding_service.embed_text(query_text)
        
        results = await self._vector_repository.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters
        )
        
        return results