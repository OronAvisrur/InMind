from typing import List, Optional
import chromadb
from chromadb.config import Settings
from pydantic import BaseModel, Field
from src.domain.models.product import Product
from src.domain.models.search_result import SearchResult

class ChromaConfig(BaseModel):
    persist_directory: str = Field(default="./data/chroma")
    collection_name: str = Field(default="products")

class ChromaVectorRepository:
    def __init__(self, config: ChromaConfig):
        self._client = chromadb.Client(Settings(
            persist_directory=config.persist_directory,
            anonymized_telemetry=False
        ))
        self._collection = self._client.get_or_create_collection(
            name=config.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    async def add_products(self, products: List[Product]) -> None:
        if not products:
            return
        
        ids = [str(product.id) for product in products]
        documents = [product.description for product in products]
        metadatas = [
            {
                "name": product.name,
                "category": product.category,
                "price": product.price,
                "brand": product.brand or "",
                "features": ",".join(product.features) if product.features else ""
            }
            for product in products
        ]
        
        self._collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
    
    async def search(
        self, 
        query_embedding: List[float], 
        top_k: int = 5,
        filters: Optional[dict] = None
    ) -> List[SearchResult]:
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filters
        )
        
        search_results = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i]
                score = 1.0 - distance
                
                features_str = metadata.get("features", "")
                features = features_str.split(",") if features_str else []
                
                product = Product(
                    id=doc_id,
                    name=metadata["name"],
                    description=results["documents"][0][i],
                    category=metadata["category"],
                    price=metadata["price"],
                    brand=metadata.get("brand") or None,
                    features=features if features else None
                )
                
                search_result = SearchResult(
                    product=product,
                    score=max(0.0, min(1.0, score)),
                    chunk_text=results["documents"][0][i],
                    metadata=metadata
                )
                search_results.append(search_result)
        
        return search_results
    
    async def delete_product(self, product_id: str) -> None:
        self._collection.delete(ids=[product_id])
    
    async def get_product_count(self) -> int:
        return self._collection.count()