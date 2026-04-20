"""Script to create all demo framework files."""
import os

BASE = os.path.join(os.path.dirname(__file__), "demo_reference_tests", "shopease_framework")

def w(rel_path, content):
    path = os.path.join(BASE, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Created: {rel_path}")

# --- Tasks ---
w("tasks/product_task.py", '''\
"""Product management tasks for ShopEasy API testing."""
import logging
LOGGER = logging.getLogger(__name__)

class ProductTask:
    """Task class for product CRUD operations."""
    @staticmethod
    def create_product(system, product_data):
        LOGGER.info("Creating product: %s", product_data.get("name", "unknown"))
        return {"result": True, "product_id": 1001, "product_details": product_data}
    @staticmethod
    def get_product_details(system, product_id):
        LOGGER.info("Getting product details for ID: %s", product_id)
        return {"id": product_id, "name": "Test Product", "price": 29.99, "status": "active"}
    @staticmethod
    def update_product(system, product_id, update_data):
        LOGGER.info("Updating product %s", product_id)
        return {"result": True, "product_details": update_data}
    @staticmethod
    def delete_product(system, product_id):
        LOGGER.info("Deleting product %s", product_id)
        return True
    @staticmethod
    def search_products(system, query="", category=None, min_price=None, max_price=None):
        LOGGER.info("Searching products: query=%s, category=%s", query, category)
        return [{"id": 1001, "name": "Test Product", "price": 29.99}]
    @staticmethod
    def get_product_inventory(system, product_id):
        return {"product_id": product_id, "quantity": 100, "warehouse": "WH-001"}
    @staticmethod
    def bulk_import_products(system, products_list):
        LOGGER.info("Bulk importing %d products", len(products_list))
        return {"result": True, "imported_count": len(products_list), "job_id": "JOB-001"}
''')

w("tasks/category_task.py", '''\
"""Category management tasks."""
import logging
LOGGER = logging.getLogger(__name__)

class CategoryTask:
    @staticmethod
    def create_category(system, category_name, parent_id=None):
        LOGGER.info("Creating category: %s", category_name)
        return {"result": True, "category_id": 501, "category_name": category_name}
    @staticmethod
    def verify_category(system, create_category_response):
        return True
    @staticmethod
    def add_verify_products_in_category(system, category_ids, product_ids):
        return True
    @staticmethod
    def get_all_categories(system):
        return [{"id": 501, "name": "Electronics"}, {"id": 502, "name": "Clothing"}]
    @staticmethod
    def delete_categories(system, category_name=None, category_id=None):
        return True
''')

w("tasks/order_task.py", '''\
"""Order management tasks."""
import logging
LOGGER = logging.getLogger(__name__)

class OrderTask:
    @staticmethod
    def create_order(system, order_data):
        LOGGER.info("Creating order for customer: %s", order_data.get("customer_id"))
        return {"result": True, "order_id": "ORD-2001", "order_details": order_data}
    @staticmethod
    def get_order_status(system, order_id):
        return {"order_id": order_id, "status": "processing", "updated_at": "2024-01-15T10:30:00"}
    @staticmethod
    def update_order_status(system, order_id, new_status):
        return {"result": True, "order_id": order_id, "status": new_status}
    @staticmethod
    def cancel_order(system, order_id, reason=""):
        return {"result": True, "order_id": order_id, "status": "cancelled"}
    @staticmethod
    def get_order_history(system, customer_id=None, status=None):
        return [{"order_id": "ORD-2001", "status": "delivered", "total": 59.99}]
    @staticmethod
    def process_refund(system, order_id, amount=None):
        return {"result": True, "refund_id": "REF-001", "status": "processed"}
''')

w("tasks/cart_task.py", '''\
"""Shopping cart tasks."""
import logging
LOGGER = logging.getLogger(__name__)

class CartTask:
    @staticmethod
    def create_cart(system, customer_id):
        return {"result": True, "cart_id": "CART-3001", "customer_id": customer_id}
    @staticmethod
    def add_item_to_cart(system, cart_id, product_id, quantity=1):
        return {"result": True, "cart_id": cart_id, "items_count": 1}
    @staticmethod
    def get_cart_details(system, cart_id):
        return {"cart_id": cart_id, "items": [], "total": 0.0}
    @staticmethod
    def remove_item_from_cart(system, cart_id, product_id):
        return True
    @staticmethod
    def clear_cart(system, cart_id):
        return True
    @staticmethod
    def checkout_cart(system, cart_id, payment_method="credit_card"):
        return {"result": True, "order_id": "ORD-2001", "status": "pending"}
''')

w("tasks/user_task.py", '''\
"""User management tasks."""
import logging
LOGGER = logging.getLogger(__name__)

class UserTask:
    @staticmethod
    def create_user(system, user_data):
        return {"result": True, "user_id": 4001, "user_details": user_data}
    @staticmethod
    def get_user_details(system, user_id):
        return {"id": user_id, "name": "Test User", "email": "test@example.com", "role": "customer"}
    @staticmethod
    def update_user(system, user_id, update_data):
        return {"result": True, "user_details": update_data}
    @staticmethod
    def delete_user(system, user_id):
        return True
    @staticmethod
    def authenticate_user(system, username, password):
        return {"result": True, "token": "eyJ...", "user_id": 4001}
    @staticmethod
    def get_user_orders(system, user_id):
        return [{"order_id": "ORD-2001", "status": "delivered"}]
''')

w("tasks/inventory_task.py", '''\
"""Inventory management tasks."""
import logging
LOGGER = logging.getLogger(__name__)

class InventoryTask:
    @staticmethod
    def check_inventory(system, product_id):
        return {"product_id": product_id, "quantity": 100, "status": "in_stock"}
    @staticmethod
    def update_inventory(system, product_id, quantity, operation="set"):
        return {"result": True, "new_quantity": quantity}
    @staticmethod
    def validate_inventory(system, product_data):
        return True
    @staticmethod
    def get_low_stock_products(system, threshold=10):
        return []
    @staticmethod
    def sync_warehouse_inventory(system, warehouse_id):
        return {"result": True, "synced_count": 50, "job_id": "SYNC-001"}
''')

w("tasks/payment_task.py", '''\
"""Payment processing tasks."""
import logging
LOGGER = logging.getLogger(__name__)

class PaymentTask:
    @staticmethod
    def process_payment(system, order_id, payment_data):
        return {"result": True, "transaction_id": "TXN-5001", "status": "approved"}
    @staticmethod
    def verify_payment(system, transaction_id):
        return {"transaction_id": transaction_id, "status": "approved", "amount": 59.99}
    @staticmethod
    def process_refund_payment(system, transaction_id, amount=None):
        return {"result": True, "refund_id": "REF-001", "status": "processed"}
    @staticmethod
    def get_payment_methods(system, customer_id):
        return [{"type": "credit_card", "last_four": "4242", "brand": "Visa"}]
''')

w("tasks/notification_task.py", '''\
"""Notification/alert management tasks."""
import logging
LOGGER = logging.getLogger(__name__)

class NotificationTask:
    @staticmethod
    def create_notification_rule(system, rule_data, event_types=None):
        return True, {"rule_id": "NR-001", "status": "active"}
    @staticmethod
    def get_notification_rules(system):
        return [{"rule_id": "NR-001", "event_type": "order_placed", "status": "active"}]
    @staticmethod
    def delete_notification_rules(system):
        return True
    @staticmethod
    def verify_notification_sent(system, event_type, timeout=30):
        return True
''')

w("tasks/report_task.py", '''\
"""Report generation tasks."""
import logging
LOGGER = logging.getLogger(__name__)

class ReportTask:
    @staticmethod
    def get_all_reports(system):
        return [{"id": "RPT-001", "name": "Sales Summary"}, {"id": "RPT-002", "name": "Inventory Report"}]
    @staticmethod
    def run_report(system, report_type="sales_summary", date_range=None):
        return {"result": True, "report_id": "RPT-RUN-001", "status": "completed"}
    @staticmethod
    def export_report(system, report_id, format="csv"):
        return {"result": True, "download_url": "/reports/RPT-RUN-001.csv"}
''')

# --- Models ---
w("models/product_service.py", '''\
"""Product API service layer."""
import logging
LOGGER = logging.getLogger(__name__)

class ProductService:
    @staticmethod
    def get_product_info(system, check_return_code=True):
        class Response:
            return_code = 200
            data = [{"Version": "3.2.1", "ProductCount": 1500, "BuildNumber": "20240115"}]
        return Response()
    @staticmethod
    def get_api_health(system):
        class Response:
            return_code = 200
            data = [{"status": "healthy", "uptime": "99.99%"}]
        return Response()
''')

w("models/order_service.py", '''\
"""Order API service layer."""
import logging
LOGGER = logging.getLogger(__name__)

class OrderService:
    @staticmethod
    def get_order_settings(system, check_return_code=False):
        class Response:
            return_code = 200
            data = [{"value": [
                {"Name": "MAX_ORDER_ITEMS", "Value": "100", "GroupName": "ORDER_SETTINGS"},
                {"Name": "AUTO_CANCEL_HOURS", "Value": "24", "GroupName": "ORDER_SETTINGS"},
                {"Name": "PAYMENT_TIMEOUT", "Value": "300", "GroupName": "PAYMENT_SETTINGS"},
            ]}]
        return Response()
    @staticmethod
    def update_order_settings(system, group_name="", name="", value="", **kwargs):
        class Response:
            return_code = 201
        return Response()
''')

w("models/shipping_service.py", '''\
"""Shipping profile service layer."""
import logging
LOGGER = logging.getLogger(__name__)

class ShippingService:
    """Shipping profile API operations."""
    pass
''')

# --- Helpers ---
w("helpers/order_config.py", '''\
"""Order configuration builder."""
import logging
LOGGER = logging.getLogger(__name__)

class OrderConfig:
    """Builds order configuration payloads."""
    def __init__(self, order_type="standard"):
        self.order_type = order_type
        self.items = []
        self.shipping_address = {}
        self.payment_method = None
    def add_item(self, product_id, quantity=1, price=None):
        self.items.append({"product_id": product_id, "quantity": quantity, "price": price})
    def set_shipping(self, address):
        self.shipping_address = address
    def set_payment(self, method="credit_card", details=None):
        self.payment_method = {"method": method, "details": details or {}}
    def generate_order_payload(self):
        return {
            "order_type": self.order_type,
            "items": self.items,
            "shipping_address": self.shipping_address,
            "payment": self.payment_method,
        }
''')

w("helpers/job_helper.py", '''\
"""Async job status helper."""
import logging
LOGGER = logging.getLogger(__name__)

class JobHelper:
    @staticmethod
    def check_job_status(system, job_id, expected_status="completed", delay=5, retry_count=60):
        LOGGER.info("Checking job %s status (expecting: %s)", job_id, expected_status)
        return True
    @staticmethod
    def wait_for_job(system, job_id, timeout=300):
        return {"job_id": job_id, "status": "completed", "result": "success"}
''')

w("helpers/data_generator.py", '''\
"""Test data generation utilities."""
import random
import string

class DataGenerator:
    @staticmethod
    def random_product(category="Electronics"):
        name = f"Test Product {random.randint(1000, 9999)}"
        return {"name": name, "price": round(random.uniform(9.99, 999.99), 2),
                "category": category, "sku": f"SKU-{random.randint(10000, 99999)}"}
    @staticmethod
    def random_user():
        suffix = "".join(random.choices(string.ascii_lowercase, k=6))
        return {"name": f"User {suffix}", "email": f"{suffix}@example.com",
                "password": "TestPass123!"}
    @staticmethod
    def random_address():
        return {"street": "123 Test St", "city": "Testville", "state": "CA",
                "zip": "90210", "country": "US"}
''')

# --- Workflows ---
w("workflows/checkout_flow.py", '''\
"""Checkout workflow."""
import logging
LOGGER = logging.getLogger(__name__)

class CheckoutFlow:
    """End-to-end checkout workflow helper."""
    @staticmethod
    def complete_checkout(system, cart_payload, payment_info):
        LOGGER.info("Running complete checkout flow")
        return True
    @staticmethod
    def verify_checkout_result(system, order_id, expected_status="confirmed"):
        return True
''')

w("workflows/catalog_sync.py", '''\
"""Product catalog sync workflow."""
import logging
LOGGER = logging.getLogger(__name__)

class CatalogSync:
    """Catalog synchronization workflow."""
    @staticmethod
    def sync_and_verify(system, catalog_config, product_types):
        LOGGER.info("Syncing product catalog")
        return True
    @staticmethod
    def full_inventory_sync(system, warehouse_id=None):
        return {"result": True, "synced_products": 150}
''')

print("\nAll framework files created successfully!")
