# app.py
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from flask import Flask, jsonify, request
import random
import time

# Initialize Sentry
sentry_sdk.init(
    dsn="https://b32e358926a5860ff92a88c64ba60a1d@o4508676888133632.ingest.us.sentry.io/4508676892590080",  # You'll get this from your Sentry account
    integrations=[FlaskIntegration()],
    enable_tracing=True,
    traces_sample_rate=1.0,  # Sample all traces for demo
    profiles_sample_rate=1.0,
    _experiments={
        "profiles_sample_rate": 1.0,
    }
)

app = Flask(__name__)

class PaymentError(Exception):
    pass

class InventoryError(Exception):
    pass

def process_payment(order_id, amount):
    # Intentionally fail some payments
    if random.random() < 0.3:  # 30% chance of failure
        sentry_sdk.set_context("payment", {
            "order_id": order_id,
            "amount": amount,
            "processor": "demo_processor"
        })
        raise PaymentError("Payment processing failed!")
    time.sleep(0.5)  # Simulate processing time
    return True

def check_inventory(items):
    # Add breadcrumb for inventory check
    sentry_sdk.add_breadcrumb(
        category='inventory',
        message=f'Checking inventory for {len(items)} items',
        level='info'
    )
    
    if random.random() < 0.2:  # 20% chance of inventory error
        raise InventoryError("Item out of stock!")
    time.sleep(0.3)
    return True

def calculate_shipping(address):
    # Demonstrate custom span
    with sentry_sdk.start_span(op="shipping.calculate") as span:
        span.set_data("address", address)
        time.sleep(0.4)  # Simulate calculation
        return "express" if random.random() > 0.5 else "standard"

@app.route('/api/orders', methods=['POST'])
def create_order():
    # Start a custom transaction
    with sentry_sdk.start_transaction(name="order.create") as transaction:
        try:
            data = request.json
            order_id = random.randint(1000, 9999)
            
            # Add order context
            sentry_sdk.set_context("order", {
                "order_id": order_id,
                "items": data.get("items", []),
                "customer": data.get("customer", {})
            })
            
            # Add breadcrumb for order creation
            sentry_sdk.add_breadcrumb(
                category='order',
                message=f'Creating order {order_id}',
                level='info'
            )

            # Process payment
            process_payment(order_id, data.get("total", 0))
            
            # Check inventory
            check_inventory(data.get("items", []))
            
            # Calculate shipping
            shipping = calculate_shipping(data.get("shipping_address"))
            
            return jsonify({
                "order_id": order_id,
                "status": "created",
                "shipping_method": shipping
            })

        except PaymentError as e:
            sentry_sdk.capture_exception(e)
            return jsonify({"error": "Payment failed"}), 400
        
        except InventoryError as e:
            sentry_sdk.capture_exception(e)
            return jsonify({"error": "Inventory check failed"}), 400
        
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return jsonify({"error": "Order creation failed"}), 500

@app.route('/api/trigger-error', methods=['GET'])
def trigger_error():
    # Demonstrate unhandled exception
    division_by_zero = 1 / 0
    return "This will never execute"

if __name__ == '__main__':
    app.run(debug=True, port=5000)