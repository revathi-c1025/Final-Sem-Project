"""
Mock ShopEasy API - Simulates the ShopEasy E-Commerce Platform
This provides a complete mock implementation for demo purposes.
"""

import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any


class MockShopEasyAPI:
    """
    Mock implementation of ShopEasy E-Commerce API.
    Simulates all endpoints needed for test execution.
    """

    def __init__(self):
        self.products = {}
        self.categories = {}
        self.orders = {}
        self.users = {}
        self.carts = {}
        self.notifications = []
        self.product_counter = 1000
        self.category_counter = 100
        self.order_counter = 5000
        self.user_counter = 2000
        self.cart_counter = 3000

        # Initialize with some sample data
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """Initialize with sample data for testing."""
        # Sample categories
        self.categories[1] = {
            "id": 1,
            "name": "Electronics",
            "description": "Electronic devices and accessories",
            "display_order": 1,
            "product_count": 5,
            "products": []
        }

        self.categories[2] = {
            "id": 2,
            "name": "Clothing",
            "description": "Apparel and fashion items",
            "display_order": 2,
            "product_count": 3,
            "products": []
        }

        # Sample products
        sample_products = [
            {"name": "Laptop Pro", "price": 999.99, "category": "Electronics", "sku": "LP-001"},
            {"name": "Wireless Mouse", "price": 29.99, "category": "Electronics", "sku": "WM-002"},
            {"name": "USB-C Hub", "price": 49.99, "category": "Electronics", "sku": "UC-003"},
            {"name": "T-Shirt", "price": 19.99, "category": "Clothing", "sku": "TS-001"},
            {"name": "Jeans", "price": 49.99, "category": "Clothing", "sku": "JN-001"},
        ]

        for product_data in sample_products:
            product_id = self.product_counter
            self.product_counter += 1

            product = {
                "id": product_id,
                "name": product_data["name"],
                "price": product_data["price"],
                "category": product_data["category"],
                "sku": product_data["sku"],
                "stock_status": "in_stock",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            self.products[product_id] = product

            # Add to category
            if product_data["category"] == "Electronics":
                self.categories[1]["products"].append(product_id)
            elif product_data["category"] == "Clothing":
                self.categories[2]["products"].append(product_id)

    # ==================== Product Endpoints ====================

    def create_product(self, product_data: Dict) -> Dict:
        """Create a new product."""
        product_id = self.product_counter
        self.product_counter += 1

        product = {
            "id": product_id,
            "name": product_data.get("name", "Unknown Product"),
            "price": product_data.get("price", 0.0),
            "category": product_data.get("category", "uncategorized"),
            "sku": product_data.get("sku", f"SKU-{product_id}"),
            "stock_status": "in_stock",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        self.products[product_id] = product

        return {
            "status_code": 201,
            "message": "Product created successfully",
            "product": product
        }

    def get_product(self, product_id: int) -> Dict:
        """Get a product by ID."""
        if product_id not in self.products:
            return {
                "status_code": 404,
                "error": "Product not found"
            }

        return {
            "status_code": 200,
            "product": self.products[product_id]
        }

    def update_product(self, product_id: int, update_data: Dict) -> Dict:
        """Update a product."""
        if product_id not in self.products:
            return {
                "status_code": 404,
                "error": "Product not found"
            }

        product = self.products[product_id]

        if "price" in update_data:
            product["price"] = update_data["price"]
        if "name" in update_data:
            product["name"] = update_data["name"]
        if "category" in update_data:
            product["category"] = update_data["category"]
        if "promo_tag" in update_data:
            product["promo_tag"] = update_data["promo_tag"]

        product["updated_at"] = datetime.now().isoformat()

        return {
            "status_code": 200,
            "message": "Product updated successfully",
            "product": product
        }

    def search_products(self, query: str = "", category: str = "",
                       min_price: float = 0, max_price: float = float('inf')) -> Dict:
        """Search products with filters."""
        results = []

        for product in self.products.values():
            # Text search
            if query and query.lower() not in product["name"].lower():
                continue

            # Category filter
            if category and product["category"] != category:
                continue

            # Price range filter
            if not (min_price <= product["price"] <= max_price):
                continue

            results.append(product)

        return {
            "status_code": 200,
            "count": len(results),
            "products": results
        }

    # ==================== Category Endpoints ====================

    def create_category(self, category_data: Dict) -> Dict:
        """Create a new category."""
        category_id = self.category_counter
        self.category_counter += 1

        category = {
            "id": category_id,
            "name": category_data.get("name", "Unknown Category"),
            "description": category_data.get("description", ""),
            "display_order": category_data.get("display_order", 0),
            "product_count": 0,
            "products": []
        }

        self.categories[category_id] = category

        return {
            "status_code": 201,
            "message": "Category created successfully",
            "category": category
        }

    def get_category(self, category_id: int) -> Dict:
        """Get a category by ID."""
        if category_id not in self.categories:
            return {
                "status_code": 404,
                "error": "Category not found"
            }

        return {
            "status_code": 200,
            "category": self.categories[category_id]
        }

    def update_category(self, category_id: int, update_data: Dict) -> Dict:
        """Update a category."""
        if category_id not in self.categories:
            return {
                "status_code": 404,
                "error": "Category not found"
            }

        category = self.categories[category_id]

        if "name" in update_data:
            category["name"] = update_data["name"]
        if "description" in update_data:
            category["description"] = update_data["description"]

        return {
            "status_code": 200,
            "message": "Category updated successfully",
            "category": category
        }

    def delete_category(self, category_id: int, reassign_to: str = "uncategorized") -> Dict:
        """Delete a category."""
        if category_id not in self.categories:
            return {
                "status_code": 404,
                "error": "Category not found"
            }

        # Reassign products
        category = self.categories[category_id]
        for product_id in category["products"]:
            if product_id in self.products:
                self.products[product_id]["category"] = reassign_to

        del self.categories[category_id]

        return {
            "status_code": 204,
            "message": "Category deleted successfully"
        }

    # ==================== Order Endpoints ====================

    def create_order(self, order_data: Dict) -> Dict:
        """Create a new order."""
        order_id = self.order_counter
        self.order_counter += 1

        order = {
            "id": order_id,
            "status": "processing",
            "payment_status": "captured",
            "total": order_data.get("total", 0.0),
            "items": order_data.get("items", []),
            "customer_id": order_data.get("customer_id", ""),
            "shipping_address": order_data.get("shipping_address", {}),
            "created_at": datetime.now().isoformat(),
            "status_history": [
                {
                    "status": "processing",
                    "timestamp": datetime.now().isoformat(),
                    "actor": "system"
                }
            ]
        }

        self.orders[order_id] = order

        return {
            "status_code": 201,
            "message": "Order created successfully",
            "order": order
        }

    def get_order(self, order_id: int) -> Dict:
        """Get an order by ID."""
        if order_id not in self.orders:
            return {
                "status_code": 404,
                "error": "Order not found"
            }

        return {
            "status_code": 200,
            "order": self.orders[order_id]
        }

    def update_order_status(self, order_id: int, status: str, **kwargs) -> Dict:
        """Update order status."""
        if order_id not in self.orders:
            return {
                "status_code": 404,
                "error": "Order not found"
            }

        order = self.orders[order_id]
        order["status"] = status

        # Add to status history
        order["status_history"].append({
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "actor": "system"
        })

        # Handle additional fields
        if "carrier_name" in kwargs:
            order["carrier"] = {
                "name": kwargs["carrier_name"],
                "tracking_number": kwargs.get("tracking_number", "")
            }

        if "signed_by" in kwargs:
            order["delivery_confirmation"] = {
                "signed_by": kwargs["signed_by"],
                "delivered_at": kwargs.get("delivered_at", datetime.now().isoformat())
            }

        return {
            "status_code": 200,
            "message": "Order status updated successfully",
            "order": order
        }

    # ==================== Cart Endpoints ====================

    def create_cart(self, user_id: str) -> Dict:
        """Create a new shopping cart."""
        cart_id = self.cart_counter
        self.cart_counter += 1

        cart = {
            "id": cart_id,
            "user_id": user_id,
            "status": "active",
            "items": [],
            "subtotal": 0.0,
            "discount_amount": 0.0,
            "total": 0.0,
            "created_at": datetime.now().isoformat()
        }

        self.carts[cart_id] = cart

        return {
            "status_code": 201,
            "message": "Cart created successfully",
            "cart": cart
        }

    def add_cart_item(self, cart_id: int, product_id: int, quantity: int) -> Dict:
        """Add an item to the cart."""
        if cart_id not in self.carts:
            return {
                "status_code": 404,
                "error": "Cart not found"
            }

        if product_id not in self.products:
            return {
                "status_code": 404,
                "error": "Product not found"
            }

        cart = self.carts[cart_id]
        product = self.products[product_id]

        # Check if item already exists
        for item in cart["items"]:
            if item["product_id"] == product_id:
                item["quantity"] += quantity
                item["line_total"] = item["quantity"] * product["price"]
                break
        else:
            cart["items"].append({
                "product_id": product_id,
                "name": product["name"],
                "price": product["price"],
                "quantity": quantity,
                "line_total": quantity * product["price"]
            })

        # Recalculate totals
        self._recalculate_cart(cart)

        return {
            "status_code": 200,
            "message": "Item added to cart successfully",
            "cart": cart
        }

    def update_cart_item(self, cart_id: int, product_id: int, quantity: int) -> Dict:
        """Update cart item quantity."""
        if cart_id not in self.carts:
            return {
                "status_code": 404,
                "error": "Cart not found"
            }

        cart = self.carts[cart_id]

        for item in cart["items"]:
            if item["product_id"] == product_id:
                item["quantity"] = quantity
                if product_id in self.products:
                    item["line_total"] = quantity * self.products[product_id]["price"]
                break

        self._recalculate_cart(cart)

        return {
            "status_code": 200,
            "message": "Cart item updated successfully",
            "cart": cart
        }

    def apply_discount(self, cart_id: int, discount_code: str) -> Dict:
        """Apply discount code to cart."""
        if cart_id not in self.carts:
            return {
                "status_code": 404,
                "error": "Cart not found"
            }

        cart = self.carts[cart_id]

        # Mock discount codes
        discounts = {
            "SAVE10": 0.10,
            "SAVE20": 0.20,
            "WELCOME": 0.15
        }

        if discount_code not in discounts:
            return {
                "status_code": 400,
                "error": "Invalid discount code"
            }

        discount_percent = discounts[discount_code]
        cart["discount_amount"] = cart["subtotal"] * discount_percent
        cart["discount_code"] = discount_code
        cart["total"] = cart["subtotal"] - cart["discount_amount"]

        return {
            "status_code": 200,
            "message": f"Discount {discount_code} applied successfully",
            "cart": cart
        }

    def _recalculate_cart(self, cart: Dict):
        """Recalculate cart totals."""
        cart["subtotal"] = sum(item["line_total"] for item in cart["items"])
        cart["total"] = cart["subtotal"] - cart.get("discount_amount", 0)

    # ==================== User Endpoints ====================

    def register_user(self, user_data: Dict) -> Dict:
        """Register a new user."""
        user_id = self.user_counter
        self.user_counter += 1

        user = {
            "id": user_id,
            "email": user_data.get("email", ""),
            "first_name": user_data.get("first_name", ""),
            "last_name": user_data.get("last_name", ""),
            "account_status": "pending_verification",
            "created_at": datetime.now().isoformat()
        }

        self.users[user_id] = user

        # Create notification
        self.notifications.append({
            "id": len(self.notifications) + 1,
            "type": "email_verification",
            "recipient": user["email"],
            "subject": "Verify your ShopEasy account",
            "sent_at": datetime.now().isoformat()
        })

        return {
            "status_code": 201,
            "message": "User registered successfully",
            "user": user
        }

    def get_user(self, user_id: int) -> Dict:
        """Get a user by ID."""
        if user_id not in self.users:
            return {
                "status_code": 404,
                "error": "User not found"
            }

        return {
            "status_code": 200,
            "user": self.users[user_id]
        }

    def update_user_profile(self, user_id: int, profile_data: Dict) -> Dict:
        """Update user profile."""
        if user_id not in self.users:
            return {
                "status_code": 404,
                "error": "User not found"
            }

        user = self.users[user_id]

        if "display_name" in profile_data:
            user["display_name"] = profile_data["display_name"]
        if "phone" in profile_data:
            user["phone"] = profile_data["phone"]
        if "preferred_currency" in profile_data:
            user["preferred_currency"] = profile_data["preferred_currency"]

        user["updated_at"] = datetime.now().isoformat()

        return {
            "status_code": 200,
            "message": "Profile updated successfully",
            "user": user
        }

    # ==================== Notification Endpoints ====================

    def get_notifications(self, user_id: str = "", notification_type: str = "") -> Dict:
        """Get notifications with optional filters."""
        results = []

        for notification in self.notifications:
            if user_id and notification.get("user_id") != user_id:
                continue
            if notification_type and notification["type"] != notification_type:
                continue

            results.append(notification)

        return {
            "status_code": 200,
            "count": len(results),
            "notifications": results
        }

    # ==================== Health Check ====================

    def health_check(self) -> Dict:
        """API health check."""
        return {
            "status_code": 200,
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0-demo",
            "components": {
                "products": len(self.products),
                "categories": len(self.categories),
                "orders": len(self.orders),
                "users": len(self.users),
                "carts": len(self.carts)
            }
        }


# Global instance
mock_api = MockShopEasyAPI()
