import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from uuid import uuid4
from src.main import app

client = TestClient(app)


@pytest.fixture
def mock_chroma_repository():
    with patch("src.api.dependencies.ChromaVectorRepository") as mock:
        mock_instance = MagicMock()
        mock_instance.add_products = AsyncMock()
        mock_instance.search_products = AsyncMock()
        mock_instance.get_product = AsyncMock()
        mock_instance.list_products = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_embedding_service():
    with patch("src.api.dependencies.OllamaEmbeddingService") as mock:
        mock_instance = MagicMock()
        mock_instance.embed_text = AsyncMock(return_value=[0.1] * 768)
        mock.return_value = mock_instance
        yield mock_instance


class TestProductIngestEndpoint:
    def test_ingest_products_success(self, mock_chroma_repository, mock_embedding_service):
        mock_chroma_repository.add_products.return_value = None
        
        products = [
            {
                "name": "Laptop Pro",
                "description": "High performance laptop",
                "price": 1299.99,
                "category": "electronics",
                "brand": "TechCorp"
            }
        ]
        
        response = client.post("/api/v1/products/ingest", json={"products": products})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 1
        assert "message" in data
    
    def test_ingest_multiple_products(self, mock_chroma_repository, mock_embedding_service):
        products = [
            {
                "name": "Product 1",
                "description": "Description 1",
                "price": 100.0,
                "category": "category1"
            },
            {
                "name": "Product 2",
                "description": "Description 2",
                "price": 200.0,
                "category": "category2"
            },
            {
                "name": "Product 3",
                "description": "Description 3",
                "price": 300.0,
                "category": "category3"
            }
        ]
        
        response = client.post("/api/v1/products/ingest", json={"products": products})
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 3
    
    def test_ingest_empty_products_list_fails(self):
        response = client.post("/api/v1/products/ingest", json={"products": []})
        
        assert response.status_code == 422
    
    def test_ingest_products_with_missing_required_fields_fails(self):
        products = [{"name": "Incomplete Product"}]
        
        response = client.post("/api/v1/products/ingest", json={"products": products})
        
        assert response.status_code == 422


class TestProductSearchEndpoint:
    def test_search_products_by_query(self, mock_chroma_repository, mock_embedding_service):
        product_id = str(uuid4())
        mock_chroma_repository.search_products.return_value = [
            MagicMock(
                id=product_id,
                name="Gaming Laptop",
                description="High-end gaming laptop",
                price=1999.99,
                category="electronics",
                brand="GameTech",
                features=["RTX 4090", "32GB RAM"],
                rating=4.8,
                in_stock=True,
                image_url=None,
                relevance_score=0.95
            )
        ]
        
        response = client.post(
            "/api/v1/products/search",
            json={"query": "gaming laptop", "limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["products"]) == 1
        assert data["products"][0]["name"] == "Gaming Laptop"
        assert data["products"][0]["relevance_score"] == 0.95
    
    def test_search_products_with_filters(self, mock_chroma_repository, mock_embedding_service):
        mock_chroma_repository.search_products.return_value = []
        
        response = client.post(
            "/api/v1/products/search",
            json={
                "query": "laptop",
                "limit": 5,
                "category": "electronics",
                "min_price": 500.0,
                "max_price": 1500.0,
                "min_rating": 4.0
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        assert isinstance(data["products"], list)
    
    def test_search_products_with_empty_query_fails(self):
        response = client.post(
            "/api/v1/products/search",
            json={"query": "", "limit": 10}
        )
        
        assert response.status_code == 422
    
    def test_search_products_returns_empty_list_when_no_results(
        self, mock_chroma_repository, mock_embedding_service
    ):
        mock_chroma_repository.search_products.return_value = []
        
        response = client.post(
            "/api/v1/products/search",
            json={"query": "nonexistent product", "limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["products"]) == 0


class TestProductListEndpoint:
    def test_list_products_with_defaults(self, mock_chroma_repository):
        product_id = str(uuid4())
        mock_chroma_repository.list_products.return_value = [
            MagicMock(
                id=product_id,
                name="Product 1",
                description="Description 1",
                price=100.0,
                category="category1",
                brand=None,
                features=[],
                rating=4.5,
                in_stock=True,
                image_url=None
            )
        ]
        
        response = client.get("/api/v1/products")
        
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        assert len(data["products"]) == 1
    
    def test_list_products_with_pagination(self, mock_chroma_repository):
        mock_chroma_repository.list_products.return_value = []
        
        response = client.get("/api/v1/products?skip=10&limit=20")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["products"], list)
    
    def test_list_products_with_invalid_pagination_fails(self):
        response = client.get("/api/v1/products?skip=-1&limit=10")
        
        assert response.status_code == 422


class TestProductGetEndpoint:
    def test_get_product_by_id_success(self, mock_chroma_repository):
        product_id = str(uuid4())
        mock_chroma_repository.get_product.return_value = MagicMock(
            id=product_id,
            name="Specific Product",
            description="Product description",
            price=599.99,
            category="electronics",
            brand="BrandName",
            features=["feature1", "feature2"],
            rating=4.7,
            in_stock=True,
            image_url="http://example.com/image.jpg"
        )
        
        response = client.get(f"/api/v1/products/{product_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == "Specific Product"
        assert data["price"] == 599.99
    
    def test_get_product_not_found(self, mock_chroma_repository):
        mock_chroma_repository.get_product.return_value = None
        
        product_id = str(uuid4())
        response = client.get(f"/api/v1/products/{product_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_get_product_with_invalid_uuid_fails(self):
        response = client.get("/api/v1/products/invalid-uuid")
        
        assert response.status_code == 422