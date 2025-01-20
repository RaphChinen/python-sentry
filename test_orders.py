# test_orders.py
import requests
import time
import random

def generate_order():
    return {
        "items": [
            {"id": random.randint(1, 100), "quantity": random.randint(1, 5)}
            for _ in range(random.randint(1, 5))
        ],
        "total": random.randint(10, 1000),
        "customer": {
            "id": random.randint(1, 1000),
            "name": f"Customer {random.randint(1, 100)}"
        },
        "shipping_address": {
            "street": f"{random.randint(1, 999)} Main St",
            "city": "Demo City",
            "country": "Demo Country"
        }
    }

def run_tests():
    # Create successful orders
    for _ in range(5):
        response = requests.post(
            'http://localhost:5000/api/orders', 
            json=generate_order()
        )
        print(f"Order creation response: {response.status_code}")
        time.sleep(1)

    # Trigger unhandled error
    try:
        response = requests.get('http://localhost:5000/api/trigger-error')
    except:
        print("Triggered unhandled error")

if __name__ == "__main__":
    run_tests()