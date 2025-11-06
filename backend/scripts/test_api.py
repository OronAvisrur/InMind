import asyncio
import httpx
from datetime import datetime


BASE_URL = "http://localhost:8000"


async def test_health_endpoints():
    print("\n=== Testing Health Endpoints ===")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"✓ GET /health: {response.status_code}")
        print(f"  Response: {response.json()}\n")
        
        response = await client.get(f"{BASE_URL}/health/ollama")
        print(f"✓ GET /health/ollama: {response.status_code}")
        print(f"  Response: {response.json()}\n")


async def test_conversation_flow():
    print("\n=== Testing Conversation Flow ===")
    async with httpx.AsyncClient() as client:
        start_data = {"user_id": "test-user-123"}
        response = await client.post(
            f"{BASE_URL}/api/v1/conversations/start",
            json=start_data
        )
        print(f"✓ POST /api/v1/conversations/start: {response.status_code}")
        start_result = response.json()
        print(f"  Response: {start_result}\n")
        
        conversation_id = start_result["conversation_id"]
        
        message_data = {
            "user_id": "test-user-123",
            "message": "I need wireless headphones under $200"
        }
        response = await client.post(
            f"{BASE_URL}/api/v1/conversations/{conversation_id}/message",
            json=message_data
        )
        print(f"✓ POST /api/v1/conversations/{conversation_id}/message: {response.status_code}")
        print(f"  Response: {response.json()}\n")
        
        response = await client.get(
            f"{BASE_URL}/api/v1/conversations/{conversation_id}"
        )
        print(f"✓ GET /api/v1/conversations/{conversation_id}: {response.status_code}")
        print(f"  Response: {response.json()}\n")
        
        end_data = {"reason": "Testing complete"}
        response = await client.post(
            f"{BASE_URL}/api/v1/conversations/{conversation_id}/end",
            json=end_data
        )
        print(f"✓ POST /api/v1/conversations/{conversation_id}/end: {response.status_code}")
        print(f"  Response: {response.json()}\n")


async def test_product_endpoints():
    print("\n=== Testing Product Endpoints ===")
    async with httpx.AsyncClient() as client:
        ingest_data = {
            "name": "Sony WH-1000XM5",
            "description": "Premium wireless noise-canceling headphones with industry-leading audio quality",
            "price": 399.99,
            "category": "Electronics",
            "brand": "Sony",
            "rating": 4.8,
            "features": ["Noise Cancellation", "Wireless", "30hr Battery", "Premium Audio"],
            "stock_quantity": 50
        }
        response = await client.post(
            f"{BASE_URL}/api/v1/products/ingest",
            json=ingest_data
        )
        print(f"✓ POST /api/v1/products/ingest: {response.status_code}")
        ingest_result = response.json()
        print(f"  Response: {ingest_result}\n")
        
        response = await client.get(f"{BASE_URL}/api/v1/products?page=1&page_size=5")
        print(f"✓ GET /api/v1/products: {response.status_code}")
        list_result = response.json()
        print(f"  Total products: {list_result['total']}\n")
        
        search_data = {
            "query": "headphones",
            "category": "Electronics",
            "max_price": 500.0,
            "min_rating": 4.0,
            "limit": 5
        }
        response = await client.post(
            f"{BASE_URL}/api/v1/products/search",
            json=search_data
        )
        print(f"✓ POST /api/v1/products/search: {response.status_code}")
        search_result = response.json()
        print(f"  Found {search_result['total_results']} products\n")
        
        if list_result["products"]:
            product_id = list_result["products"][0]["id"]
            response = await client.get(f"{BASE_URL}/api/v1/products/{product_id}")
            print(f"✓ GET /api/v1/products/{product_id}: {response.status_code}")
            print(f"  Product: {response.json()['name']}\n")


async def test_intent_endpoint():
    print("\n=== Testing Intent Detection ===")
    async with httpx.AsyncClient() as client:
        intent_data = {
            "text": "Show me laptops under $1000 with good battery life",
            "context": {
                "category": ["Electronics"],
                "price_range": ["under $1000"]
            }
        }
        response = await client.post(
            f"{BASE_URL}/api/v1/intents/detect",
            json=intent_data
        )
        print(f"✓ POST /api/v1/intents/detect: {response.status_code}")
        print(f"  Response: {response.json()}\n")


async def test_error_handling():
    print("\n=== Testing Error Handling ===")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/conversations/invalid-id"
        )
        print(f"✓ GET invalid conversation: {response.status_code}")
        print(f"  Error: {response.json()}\n")
        
        response = await client.get(
            f"{BASE_URL}/api/v1/products/non-existent-id"
        )
        print(f"✓ GET non-existent product: {response.status_code}")
        print(f"  Error: {response.json()}\n")
        
        invalid_data = {
            "user_id": "",
            "message": ""
        }
        response = await client.post(
            f"{BASE_URL}/api/v1/conversations/test/message",
            json=invalid_data
        )
        print(f"✓ POST invalid message: {response.status_code}")
        print(f"  Error: {response.json()}\n")


async def main():
    print("=" * 60)
    print("InMind API Test Suite")
    print("=" * 60)
    
    try:
        await test_health_endpoints()
        await test_product_endpoints()
        await test_intent_endpoint()
        await test_conversation_flow()
        await test_error_handling()
        
        print("\n" + "=" * 60)
        print("✅ All API tests completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
