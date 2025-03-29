import asyncio
import httpx
import os
import time

async def test_api():
    """Test the FAQ API endpoints"""
    # Increase timeout to 60 seconds to allow for slower processing
    async with httpx.AsyncClient(base_url="http://localhost:8081", timeout=60.0) as client:
        # Test 0: First check if the server is responding
        print("\n=== Testing API Health ===")
        try:
            response = await client.get('/')
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error connecting to API server: {str(e)}")
            return
            
        # Test 1: Add a simple FAQ
        print("\n=== Testing Add FAQ ===")
        try:
            response = await client.post('/api/v1/faq/add', json={
                "topic": "Testing",
                "question": "Is this a test question?",
                "answer": "Yes, this is a test question for the FAQ API.",
                "tags": ["test", "api"],
                "source": "API Test",
                "is_published": True,
                "priority": 1
            })
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            
            # If the add was successful, get the FAQ ID
            if response.status_code == 200:
                faq_id = response.json()["data"]["id"]
                
                # Test retrieving the FAQ by ID
                print("\n=== Testing Get FAQ by ID ===")
                response = await client.get(f'/api/v1/faq/{faq_id}')
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"Response: {response.json()}")
                else:
                    print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error adding FAQ: {str(e)}")

        # Test 2: Get Topics
        print("\n=== Testing Get Topics ===")
        try:
            response = await client.get('/api/v1/faq/topics')
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.json()}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error getting topics: {str(e)}")
            
        # Test 3: Get Sources
        print("\n=== Testing Get Sources ===")
        try:
            response = await client.get('/api/v1/faq/sources')
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.json()}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error getting sources: {str(e)}")
            
        # Test 4: Search FAQs - general query
        print("\n=== Testing FAQ Search - General Query ===")
        try:
            response = await client.post('/api/v1/faq/search', json={
                "query": "program structure",
                "limit": 5,
                "min_score": 0.3
            })
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.json()}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error searching FAQs: {str(e)}")

if __name__ == "__main__":
    print("Starting API tests... Make sure the server is running on http://localhost:8081")
    try:
        asyncio.run(test_api())
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
    except Exception as e:
        print(f"\nError running tests: {str(e)}")
    print("\nAPI tests completed") 