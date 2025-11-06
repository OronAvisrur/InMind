from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from typing import Optional
from src.api.schemas import (
    ProductResponse,
    ProductListResponse,
    ProductSearchRequest,
    ProductSearchResponse,
    ProductIngestRequest,
    ProductIngestResponse,
)
from src.api.dependencies import (
    get_vector_repository,
    get_product_ingestion_service,
)
from src.infrastructure.vector_store.chroma_repository import ChromaVectorRepository
from src.application.services.product_ingestion import ProductIngestionService
from src.domain.models.product import Product
from src.domain.value_objects.identifiers import ProductId
from src.domain.models.search_result import SearchFilters


router = APIRouter(prefix="/api/v1/products", tags=["Products"])


@router.post("/ingest", response_model=ProductIngestResponse)
async def ingest_product(
    request: ProductIngestRequest,
    ingestion_service: ProductIngestionService = Depends(get_product_ingestion_service),
):
    try:
        product = Product(
            id=ProductId.generate(),
            name=request.name,
            description=request.description,
            price=request.price,
            category=request.category,
            brand=request.brand,
            rating=request.rating,
            features=request.features,
            stock_quantity=request.stock_quantity,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        await ingestion_service.ingest_product(product)
        
        return ProductIngestResponse(
            product_id=str(product.id.value),
            status="success",
            message=f"Product '{product.name}' ingested successfully",
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest product: {str(e)}"
        )


@router.post("/search", response_model=ProductSearchResponse)
async def search_products(
    request: ProductSearchRequest,
    vector_repo: ChromaVectorRepository = Depends(get_vector_repository),
):
    try:
        filters = SearchFilters(
            categories=[request.category] if request.category else None,
            brands=[request.brand] if request.brand else None,
            min_price=request.min_price,
            max_price=request.max_price,
            min_rating=request.min_rating
        )
        
        if request.query:
            search_result = await vector_repo.similarity_search(
                query_text=request.query,
                k=request.limit,
                filters=filters
            )
            products = search_result.products
        else:
            all_results = await vector_repo.similarity_search(
                query_text="product",
                k=100,
                filters=filters
            )
            products = all_results.products[:request.limit]
        
        product_responses = [
            ProductResponse(
                id=str(product.id.value),
                name=product.name,
                description=product.description,
                price=product.price,
                category=product.category,
                brand=product.brand,
                rating=product.rating,
                features=product.features,
                stock_quantity=product.stock_quantity,
                created_at=product.created_at
            )
            for product in products
        ]
        
        return ProductSearchResponse(
            products=product_responses,
            query=request.query,
            total_results=len(product_responses),
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search products: {str(e)}"
        )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    vector_repo: ChromaVectorRepository = Depends(get_vector_repository),
):
    try:
        search_result = await vector_repo.similarity_search(
            query_text="product",
            k=100
        )
        
        product = next(
            (p for p in search_result.products if str(p.id.value) == product_id),
            None
        )
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return ProductResponse(
            id=str(product.id.value),
            name=product.name,
            description=product.description,
            price=product.price,
            category=product.category,
            brand=product.brand,
            rating=product.rating,
            features=product.features,
            stock_quantity=product.stock_quantity,
            created_at=product.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get product: {str(e)}"
        )


@router.get("/", response_model=ProductListResponse)
async def list_products(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    vector_repo: ChromaVectorRepository = Depends(get_vector_repository),
):
    try:
        search_result = await vector_repo.similarity_search(
            query_text="product",
            k=1000
        )
        
        total = len(search_result.products)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_products = search_result.products[start_idx:end_idx]
        
        product_responses = [
            ProductResponse(
                id=str(product.id.value),
                name=product.name,
                description=product.description,
                price=product.price,
                category=product.category,
                brand=product.brand,
                rating=product.rating,
                features=product.features,
                stock_quantity=product.stock_quantity,
                created_at=product.created_at
            )
            for product in paginated_products
        ]
        
        return ProductListResponse(
            products=product_responses,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list products: {str(e)}"
        )
