import pytest
from src.domain.models import Product
from src.domain.value_objects import ProductIdentifier


class TestProduct:
    def test_create_product_with_valid_data(self):
        product = Product(
            name="Test Product",
            description="A test product",
            category="Electronics",
            price=99.99,
            brand="TestBrand",
        )
        assert product.name == "Test Product"
        assert product.price == 99.99
        assert product.is_available is True

    def test_product_price_must_be_positive(self):
        with pytest.raises(ValueError):
            Product(
                name="Invalid Product",
                description="Test",
                category="Test",
                price=-10.0,
            )

    def test_product_to_document(self):
        product = Product(
            name="Laptop",
            description="Powerful laptop",
            category="Computers",
            price=1299.99,
            brand="TechCorp",
            features=["16GB RAM", "SSD"],
        )
        doc = product.to_document()
        assert "Laptop" in doc
        assert "1299.99" in doc
        assert "16GB RAM" in doc

    def test_product_strips_whitespace(self):
        product = Product(
            name="  Laptop  ",
            description="  Description  ",
            category="  Electronics  ",
            price=999.99,
        )
        assert product.name == "Laptop"
        assert product.description == "Description"
        assert product.category == "Electronics"

    def test_product_has_unique_identifier(self):
        product1 = Product(
            name="Product 1",
            description="First product",
            category="Test",
            price=10.0,
        )
        product2 = Product(
            name="Product 2",
            description="Second product",
            category="Test",
            price=20.0,
        )
        assert product1.id != product2.id