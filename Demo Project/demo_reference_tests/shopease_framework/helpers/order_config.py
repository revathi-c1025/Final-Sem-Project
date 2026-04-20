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
