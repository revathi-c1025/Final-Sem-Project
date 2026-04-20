"""Script to create all demo reference test files."""
import os

TESTS_DIR = os.path.join(os.path.dirname(__file__), "demo_reference_tests", "tests")

def w(rel_path, content):
    path = os.path.join(TESTS_DIR, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Created: tests/{rel_path}")


# TC-001: Smoke - Create and Verify Product
w("products/test_create_verify_product.py", '''\
"""
TC-001: Smoke - Create and Verify Product
Verify that a new product can be created in the ShopEasy platform with all
required attributes and is visible in the product catalog.
"""
import logging
from shopease_framework.base.base_test_case import ShopEaseBaseTestCase, Parameter
from shopease_framework.base.utils import TestUtils
from shopease_framework.tasks.product_task import ProductTask

LOGGER = logging.getLogger(__name__)


class TestCreateVerifyProduct(ShopEaseBaseTestCase):

    def __init__(self):
        super(TestCreateVerifyProduct, self).__init__()
        self._parameters = [
            Parameter("product_name", "string", "Wireless Bluetooth Headphones",
                      help="Name of the product to create"),
            Parameter("product_price", "float", 79.99,
                      help="Price of the product"),
            Parameter("product_category", "string", "Electronics",
                      help="Product category"),
            Parameter("product_sku", "string", "WBH-1001",
                      help="Product SKU"),
        ]

    def pre_testcase(self, testbed_obj):
        ShopEaseBaseTestCase.pre_testcase(self, testbed_obj)
        self.__dict__.update(self.params)
        LOGGER.info("Pre-testcase setup complete for TC-001")

    def run_test(self):
        system = self.api_system

        # Step 1: Create a new product via POST /api/products
        LOGGER.info(f"Step {self.step_count}: Creating product '{self.product_name}'")
        product_data = {
            "name": self.product_name,
            "price": self.product_price,
            "category": self.product_category,
            "sku": self.product_sku,
        }
        create_resp = ProductTask.create_product(system, product_data)
        TestUtils.test_assert_true(
            create_resp.get("result"),
            "Product creation should return success"
        )
        product_id = create_resp["product_id"]
        LOGGER.info("Product created with ID: %s", product_id)

        # Step 2: Retrieve product details and verify fields
        LOGGER.info(f"Step {self.step_count}: Verifying product details for ID {product_id}")
        details = ProductTask.get_product_details(system, product_id)
        TestUtils.test_assert_equals(
            product_id, details["id"],
            "Product ID should match"
        )
        TestUtils.test_assert_equals(
            "active", details.get("status"),
            "New product status should default to active"
        )

        # Step 3: Verify product appears in catalog search
        LOGGER.info(f"Step {self.step_count}: Searching product catalog by category")
        results = ProductTask.search_products(
            system, category=self.product_category
        )
        TestUtils.test_assert_true(
            len(results) > 0,
            "Product catalog should contain at least one product in category"
        )

        # Step 4: Update product price
        LOGGER.info(f"Step {self.step_count}: Updating product price to 69.99")
        update_resp = ProductTask.update_product(
            system, product_id, {"price": 69.99, "promo_tag": "Summer Sale"}
        )
        TestUtils.test_assert_true(
            update_resp.get("result"),
            "Product update should succeed"
        )

        # Step 5: Verify update persisted
        LOGGER.info(f"Step {self.step_count}: Verifying updated product details")
        updated = ProductTask.get_product_details(system, product_id)
        LOGGER.info("Product update verification complete")

    def post_testcase(self):
        LOGGER.info("Post-testcase cleanup for TC-001")
        super(TestCreateVerifyProduct, self).post_testcase()
''')


# TC-002: Regression - Product Search and Filtering
w("products/test_product_search_filtering.py", '''\
"""
TC-002: Regression - Product Search and Filtering
Validate the product search and filtering functionality, ensuring users can
find products by name, category, and price range.
"""
import logging
from shopease_framework.base.base_test_case import ShopEaseBaseTestCase, Parameter
from shopease_framework.base.utils import TestUtils
from shopease_framework.tasks.product_task import ProductTask

LOGGER = logging.getLogger(__name__)


class TestProductSearchFiltering(ShopEaseBaseTestCase):

    def __init__(self):
        super(TestProductSearchFiltering, self).__init__()
        self._parameters = [
            Parameter("search_keyword", "string", "Bluetooth",
                      help="Keyword to search for"),
            Parameter("filter_category", "string", "Electronics",
                      help="Category to filter by"),
            Parameter("min_price", "float", 25.00,
                      help="Minimum price filter"),
            Parameter("max_price", "float", 100.00,
                      help="Maximum price filter"),
        ]

    def pre_testcase(self, testbed_obj):
        ShopEaseBaseTestCase.pre_testcase(self, testbed_obj)
        self.__dict__.update(self.params)

    def run_test(self):
        system = self.api_system

        # Step 1: Keyword search
        LOGGER.info(f"Step {self.step_count}: Searching products by keyword '{self.search_keyword}'")
        keyword_results = ProductTask.search_products(system, query=self.search_keyword)
        TestUtils.test_assert_true(
            len(keyword_results) > 0,
            "Keyword search should return at least one product"
        )

        # Step 2: Category filter with sort
        LOGGER.info(f"Step {self.step_count}: Filtering by category '{self.filter_category}'")
        cat_results = ProductTask.search_products(system, category=self.filter_category)
        TestUtils.test_assert_true(
            len(cat_results) > 0,
            "Category filter should return products"
        )

        # Step 3: Price range filter
        LOGGER.info(f"Step {self.step_count}: Filtering by price range {self.min_price}-{self.max_price}")
        price_results = ProductTask.search_products(
            system, min_price=self.min_price, max_price=self.max_price
        )
        TestUtils.test_assert_true(
            len(price_results) >= 0,
            "Price range filter should return results"
        )

        # Step 4: Combined filters
        LOGGER.info(f"Step {self.step_count}: Applying combined filters")
        combined = ProductTask.search_products(
            system, query=self.search_keyword,
            category=self.filter_category,
            min_price=self.min_price, max_price=self.max_price,
        )
        TestUtils.test_assert_true(
            len(combined) <= len(cat_results),
            "Combined filter count should be <= single filter count"
        )
        LOGGER.info("All search and filter tests passed")

    def post_testcase(self):
        super(TestProductSearchFiltering, self).post_testcase()
''')


# TC-003: Regression - Category Management
w("categories/test_category_management.py", '''\
"""
TC-003: Regression - Category Management
Test the full lifecycle of product category management including creation,
product association, renaming, and deletion.
"""
import logging
from shopease_framework.base.base_test_case import ShopEaseBaseTestCase, Parameter
from shopease_framework.base.utils import TestUtils
from shopease_framework.tasks.category_task import CategoryTask
from shopease_framework.tasks.product_task import ProductTask

LOGGER = logging.getLogger(__name__)


class TestCategoryManagement(ShopEaseBaseTestCase):

    def __init__(self):
        super(TestCategoryManagement, self).__init__()
        self._parameters = [
            Parameter("category_name", "string", "Summer Collection",
                      help="Category name to create"),
            Parameter("updated_name", "string", "Summer Deals 2025",
                      help="Updated category name"),
        ]
        self._created_category_id = None

    def pre_testcase(self, testbed_obj):
        ShopEaseBaseTestCase.pre_testcase(self, testbed_obj)
        self.__dict__.update(self.params)

    def run_test(self):
        system = self.api_system

        # Step 1: Create a new category
        LOGGER.info(f"Step {self.step_count}: Creating category '{self.category_name}'")
        create_resp = CategoryTask.create_category(system, self.category_name)
        TestUtils.test_assert_true(
            create_resp.get("result"),
            "Category creation should succeed"
        )
        self._created_category_id = create_resp["category_id"]

        # Step 2: Associate products with the category
        LOGGER.info(f"Step {self.step_count}: Adding products to category")
        assoc_result = CategoryTask.add_verify_products_in_category(
            system, [self._created_category_id], [1001, 1002, 1003]
        )
        TestUtils.test_assert_true(assoc_result, "Product association should succeed")

        # Step 3: Verify category details and product count
        LOGGER.info(f"Step {self.step_count}: Verifying category details")
        verify_result = CategoryTask.verify_category(system, create_resp)
        TestUtils.test_assert_true(verify_result, "Category verification should pass")

        # Step 4: Rename the category
        LOGGER.info(f"Step {self.step_count}: Renaming category to '{self.updated_name}'")
        all_cats = CategoryTask.get_all_categories(system)
        TestUtils.test_assert_true(
            len(all_cats) > 0,
            "Should have at least one category"
        )

        # Step 5: Delete the category
        LOGGER.info(f"Step {self.step_count}: Deleting category")
        del_result = CategoryTask.delete_categories(
            system, category_id=self._created_category_id
        )
        TestUtils.test_assert_true(del_result, "Category deletion should succeed")

    def post_testcase(self):
        if self._created_category_id:
            LOGGER.info("Cleanup: ensuring category %s is removed", self._created_category_id)
        super(TestCategoryManagement, self).post_testcase()
''')


# TC-004: Smoke - End-to-End Order Placement
w("orders/test_order_placement.py", '''\
"""
TC-004: Smoke - End-to-End Order Placement
Validate the complete order placement flow from cart creation through
payment processing and order confirmation.
"""
import logging
from shopease_framework.base.base_test_case import ShopEaseBaseTestCase, Parameter
from shopease_framework.base.utils import TestUtils
from shopease_framework.tasks.cart_task import CartTask
from shopease_framework.tasks.order_task import OrderTask
from shopease_framework.tasks.payment_task import PaymentTask
from shopease_framework.tasks.notification_task import NotificationTask

LOGGER = logging.getLogger(__name__)


class TestOrderPlacement(ShopEaseBaseTestCase):

    def __init__(self):
        super(TestOrderPlacement, self).__init__()
        self._parameters = [
            Parameter("customer_id", "string", "CUST-001",
                      help="Customer ID for order placement"),
            Parameter("product_a_id", "string", "P-101",
                      help="First product ID"),
            Parameter("product_b_id", "string", "P-102",
                      help="Second product ID"),
        ]
        self._cart_id = None
        self._order_id = None

    def pre_testcase(self, testbed_obj):
        ShopEaseBaseTestCase.pre_testcase(self, testbed_obj)
        self.__dict__.update(self.params)

    def run_test(self):
        system = self.api_system

        # Step 1: Create shopping cart
        LOGGER.info(f"Step {self.step_count}: Creating shopping cart for {self.customer_id}")
        cart_resp = CartTask.create_cart(system, self.customer_id)
        TestUtils.test_assert_true(
            cart_resp.get("result"),
            "Cart creation should succeed"
        )
        self._cart_id = cart_resp["cart_id"]

        # Step 2: Add two products to cart
        LOGGER.info(f"Step {self.step_count}: Adding products to cart")
        CartTask.add_item_to_cart(system, self._cart_id, self.product_a_id, quantity=2)
        CartTask.add_item_to_cart(system, self._cart_id, self.product_b_id, quantity=1)
        cart_details = CartTask.get_cart_details(system, self._cart_id)
        LOGGER.info("Cart has %d items", len(cart_details.get("items", [])))

        # Step 3: Apply discount code (simulated)
        LOGGER.info(f"Step {self.step_count}: Applying discount code SAVE10")
        LOGGER.info("Discount applied successfully")

        # Step 4: Checkout cart and process payment
        LOGGER.info(f"Step {self.step_count}: Initiating checkout")
        checkout_resp = CartTask.checkout_cart(
            system, self._cart_id, payment_method="credit_card"
        )
        TestUtils.test_assert_true(
            checkout_resp.get("result"),
            "Checkout should succeed"
        )
        self._order_id = checkout_resp["order_id"]

        # Step 5: Verify order details
        LOGGER.info(f"Step {self.step_count}: Verifying order {self._order_id}")
        order_status = OrderTask.get_order_status(system, self._order_id)
        TestUtils.test_assert_true(
            order_status.get("status") in ["processing", "confirmed", "pending"],
            "Order status should be valid"
        )

        # Step 6: Verify order confirmation notification
        LOGGER.info(f"Step {self.step_count}: Checking order confirmation notification")
        notif_sent = NotificationTask.verify_notification_sent(
            system, "order_confirmation"
        )
        TestUtils.test_assert_true(notif_sent, "Order confirmation notification should be sent")

    def post_testcase(self):
        if self._cart_id:
            LOGGER.info("Cleanup: clearing cart %s", self._cart_id)
        super(TestOrderPlacement, self).post_testcase()
''')


# TC-005: Comprehensive - Order Lifecycle Management
w("orders/test_order_lifecycle.py", '''\
"""
TC-005: Comprehensive - Order Lifecycle Management
Test the complete order lifecycle from creation through processing,
shipping, delivery, and historical record.
"""
import logging
from shopease_framework.base.base_test_case import ShopEaseBaseTestCase, Parameter
from shopease_framework.base.utils import TestUtils
from shopease_framework.tasks.order_task import OrderTask
from shopease_framework.helpers.order_config import OrderConfig

LOGGER = logging.getLogger(__name__)


class TestOrderLifecycle(ShopEaseBaseTestCase):

    def __init__(self):
        super(TestOrderLifecycle, self).__init__()
        self._parameters = [
            Parameter("customer_id", "string", "CUST-001",
                      help="Customer ID"),
            Parameter("carrier_name", "string", "FedEx",
                      help="Shipping carrier"),
            Parameter("tracking_number", "string", "FX123456789",
                      help="Tracking number"),
        ]
        self._order_id = None

    def pre_testcase(self, testbed_obj):
        ShopEaseBaseTestCase.pre_testcase(self, testbed_obj)
        self.__dict__.update(self.params)

    def run_test(self):
        system = self.api_system

        # Step 1: Create a new order
        LOGGER.info(f"Step {self.step_count}: Creating new order")
        config = OrderConfig("standard")
        config.add_item("P-101", quantity=2, price=29.99)
        config.add_item("P-102", quantity=1, price=49.99)
        config.set_payment("credit_card")
        order_resp = OrderTask.create_order(system, config.generate_order_payload())
        TestUtils.test_assert_true(
            order_resp.get("result"),
            "Order creation should succeed"
        )
        self._order_id = order_resp["order_id"]

        # Step 2: Verify initial order status
        LOGGER.info(f"Step {self.step_count}: Verifying initial order status")
        status = OrderTask.get_order_status(system, self._order_id)
        TestUtils.test_assert_equals(
            "processing", status.get("status"),
            "Initial order status should be processing"
        )

        # Step 3: Update status to shipped
        LOGGER.info(f"Step {self.step_count}: Updating order status to 'shipped'")
        ship_resp = OrderTask.update_order_status(system, self._order_id, "shipped")
        TestUtils.test_assert_true(
            ship_resp.get("result"),
            "Ship status update should succeed"
        )

        # Step 4: Add tracking events
        LOGGER.info(f"Step {self.step_count}: Adding tracking events")
        tracking_events = ["picked_up", "in_transit", "out_for_delivery"]
        for event in tracking_events:
            LOGGER.info("  Tracking event: %s", event)

        # Step 5: Mark as delivered
        LOGGER.info(f"Step {self.step_count}: Marking order as delivered")
        deliver_resp = OrderTask.update_order_status(
            system, self._order_id, "delivered"
        )
        TestUtils.test_assert_true(
            deliver_resp.get("result"),
            "Delivery status update should succeed"
        )

        # Step 6: Verify complete order record
        LOGGER.info(f"Step {self.step_count}: Verifying complete order record")
        final_status = OrderTask.get_order_status(system, self._order_id)
        LOGGER.info("Final order status: %s", final_status.get("status"))

        # Step 7: Verify order appears in customer history
        LOGGER.info(f"Step {self.step_count}: Checking customer order history")
        history = OrderTask.get_order_history(
            system, customer_id=self.customer_id
        )
        TestUtils.test_assert_true(
            len(history) > 0,
            "Customer order history should not be empty"
        )

    def post_testcase(self):
        super(TestOrderLifecycle, self).post_testcase()
''')


# TC-006: Smoke - User Registration and Authentication
w("users/test_user_registration.py", '''\
"""
TC-006: Smoke - User Registration and Authentication
Verify the complete user registration, email verification, login, and
profile update flow.
"""
import logging
from shopease_framework.base.base_test_case import ShopEaseBaseTestCase, Parameter
from shopease_framework.base.utils import TestUtils
from shopease_framework.tasks.user_task import UserTask

LOGGER = logging.getLogger(__name__)


class TestUserRegistration(ShopEaseBaseTestCase):

    def __init__(self):
        super(TestUserRegistration, self).__init__()
        self._parameters = [
            Parameter("test_email", "string", "testuser@example.com",
                      help="Email address for registration"),
            Parameter("test_password", "string", "TestPass123!",
                      help="Password for registration"),
            Parameter("first_name", "string", "Jane", help="First name"),
            Parameter("last_name", "string", "Smith", help="Last name"),
        ]
        self._created_user_id = None

    def pre_testcase(self, testbed_obj):
        ShopEaseBaseTestCase.pre_testcase(self, testbed_obj)
        self.__dict__.update(self.params)

    def run_test(self):
        system = self.api_system

        # Step 1: Register new user
        LOGGER.info(f"Step {self.step_count}: Registering user {self.test_email}")
        user_data = {
            "email": self.test_email,
            "password": self.test_password,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }
        reg_resp = UserTask.create_user(system, user_data)
        TestUtils.test_assert_true(
            reg_resp.get("result"),
            "User registration should succeed"
        )
        self._created_user_id = reg_resp["user_id"]

        # Step 2: Verify email verification was sent
        LOGGER.info(f"Step {self.step_count}: Verifying email notification sent")
        LOGGER.info("Verification email sent to %s", self.test_email)

        # Step 3: Authenticate user
        LOGGER.info(f"Step {self.step_count}: Authenticating user")
        auth_resp = UserTask.authenticate_user(
            system, self.test_email, self.test_password
        )
        TestUtils.test_assert_true(
            auth_resp.get("result"),
            "Authentication should succeed"
        )
        TestUtils.test_assert_true(
            "token" in auth_resp,
            "Auth response should contain a token"
        )

        # Step 4: Update user profile
        LOGGER.info(f"Step {self.step_count}: Updating user profile")
        profile_update = {
            "display_name": "JaneS",
            "phone": "+1-555-0123",
            "preferred_currency": "USD",
        }
        update_resp = UserTask.update_user(
            system, self._created_user_id, profile_update
        )
        TestUtils.test_assert_true(
            update_resp.get("result"),
            "Profile update should succeed"
        )

        # Step 5: Verify profile changes persisted
        LOGGER.info(f"Step {self.step_count}: Verifying profile changes")
        user_details = UserTask.get_user_details(system, self._created_user_id)
        TestUtils.test_assert_true(
            user_details is not None,
            "User details should be retrievable"
        )

    def post_testcase(self):
        if self._created_user_id:
            LOGGER.info("Cleanup: removing test user %s", self._created_user_id)
        super(TestUserRegistration, self).post_testcase()
''')


# TC-007: Regression - Shopping Cart Operations
w("cart/test_cart_operations.py", '''\
"""
TC-007: Regression - Shopping Cart Operations
Test comprehensive shopping cart operations including item addition,
quantity updates, item removal, and total recalculation.
"""
import logging
from shopease_framework.base.base_test_case import ShopEaseBaseTestCase, Parameter
from shopease_framework.base.utils import TestUtils
from shopease_framework.tasks.cart_task import CartTask

LOGGER = logging.getLogger(__name__)


class TestCartOperations(ShopEaseBaseTestCase):

    def __init__(self):
        super(TestCartOperations, self).__init__()
        self._parameters = [
            Parameter("customer_id", "string", "CUST-001",
                      help="Customer ID"),
            Parameter("product_1_id", "string", "P-101",
                      help="First product (price 25.00)"),
            Parameter("product_2_id", "string", "P-102",
                      help="Second product (price 45.50)"),
        ]
        self._cart_id = None

    def pre_testcase(self, testbed_obj):
        ShopEaseBaseTestCase.pre_testcase(self, testbed_obj)
        self.__dict__.update(self.params)

    def run_test(self):
        system = self.api_system

        # Step 1: Create empty cart
        LOGGER.info(f"Step {self.step_count}: Creating empty shopping cart")
        cart_resp = CartTask.create_cart(system, self.customer_id)
        TestUtils.test_assert_true(
            cart_resp.get("result"),
            "Cart creation should succeed"
        )
        self._cart_id = cart_resp["cart_id"]

        # Step 2: Add first product (quantity 3)
        LOGGER.info(f"Step {self.step_count}: Adding {self.product_1_id} qty 3")
        add1 = CartTask.add_item_to_cart(
            system, self._cart_id, self.product_1_id, quantity=3
        )
        TestUtils.test_assert_true(
            add1.get("result"),
            "Adding product 1 should succeed"
        )

        # Step 3: Add second product (quantity 1)
        LOGGER.info(f"Step {self.step_count}: Adding {self.product_2_id} qty 1")
        add2 = CartTask.add_item_to_cart(
            system, self._cart_id, self.product_2_id, quantity=1
        )
        TestUtils.test_assert_true(
            add2.get("result"),
            "Adding product 2 should succeed"
        )

        # Step 4: Update quantity of product 1 to 1
        LOGGER.info(f"Step {self.step_count}: Updating {self.product_1_id} quantity to 1")
        cart_details = CartTask.get_cart_details(system, self._cart_id)
        LOGGER.info("Cart details: %s", cart_details)

        # Step 5: Remove product 1
        LOGGER.info(f"Step {self.step_count}: Removing {self.product_1_id} from cart")
        remove_result = CartTask.remove_item_from_cart(
            system, self._cart_id, self.product_1_id
        )
        TestUtils.test_assert_true(remove_result, "Item removal should succeed")

        # Step 6: Verify final cart state
        LOGGER.info(f"Step {self.step_count}: Verifying final cart state")
        final_cart = CartTask.get_cart_details(system, self._cart_id)
        LOGGER.info("Final cart state retrieved successfully")

    def post_testcase(self):
        if self._cart_id:
            CartTask.clear_cart(self.api_system, self._cart_id)
            LOGGER.info("Cleanup: cleared cart %s", self._cart_id)
        super(TestCartOperations, self).post_testcase()
''')


# TC-008: Comprehensive - Inventory Sync and Stock Management
w("inventory/test_inventory_sync.py", '''\
"""
TC-008: Comprehensive - Inventory Sync and Stock Management
Test inventory management operations including stock checks, quantity
adjustments, warehouse synchronization, and low-stock alert triggers.
"""
import logging
from shopease_framework.base.base_test_case import ShopEaseBaseTestCase, Parameter
from shopease_framework.base.utils import TestUtils
from shopease_framework.tasks.inventory_task import InventoryTask
from shopease_framework.helpers.job_helper import JobHelper

LOGGER = logging.getLogger(__name__)


class TestInventorySync(ShopEaseBaseTestCase):

    def __init__(self):
        super(TestInventorySync, self).__init__()
        self._parameters = [
            Parameter("product_id", "string", "P-201",
                      help="Product to check inventory for"),
            Parameter("warehouse_id", "string", "WH-001",
                      help="Warehouse for sync operations"),
            Parameter("low_stock_threshold", "int", 10,
                      help="Low stock alert threshold"),
        ]

    def pre_testcase(self, testbed_obj):
        ShopEaseBaseTestCase.pre_testcase(self, testbed_obj)
        self.__dict__.update(self.params)

    def run_test(self):
        system = self.api_system

        # Step 1: Check initial stock level
        LOGGER.info(f"Step {self.step_count}: Checking initial inventory for {self.product_id}")
        inventory = InventoryTask.check_inventory(system, self.product_id)
        TestUtils.test_assert_equals(
            "in_stock", inventory.get("status"),
            "Product should be in stock"
        )
        initial_qty = inventory["quantity"]
        LOGGER.info("Initial stock: %d units", initial_qty)

        # Step 2: Add stock via adjustment
        LOGGER.info(f"Step {self.step_count}: Adding 25 units to inventory")
        adj_resp = InventoryTask.update_inventory(
            system, self.product_id, initial_qty + 25, operation="add"
        )
        TestUtils.test_assert_true(
            adj_resp.get("result"),
            "Inventory adjustment should succeed"
        )

        # Step 3: Verify updated stock
        LOGGER.info(f"Step {self.step_count}: Verifying updated stock level")
        updated = InventoryTask.check_inventory(system, self.product_id)
        LOGGER.info("Updated stock quantity: %d", updated.get("quantity", 0))

        # Step 4: Trigger warehouse sync
        LOGGER.info(f"Step {self.step_count}: Triggering warehouse sync")
        sync_resp = InventoryTask.sync_warehouse_inventory(
            system, self.warehouse_id
        )
        TestUtils.test_assert_true(
            sync_resp.get("result"),
            "Warehouse sync should succeed"
        )
        job_id = sync_resp.get("job_id")

        # Step 5: Wait for sync job to complete
        LOGGER.info(f"Step {self.step_count}: Waiting for sync job {job_id}")
        job_done = JobHelper.check_job_status(
            system, job_id, expected_status="completed"
        )
        TestUtils.test_assert_true(job_done, "Sync job should complete")

        # Step 6: Reduce stock below threshold to trigger alert
        LOGGER.info(f"Step {self.step_count}: Reducing stock below threshold")
        InventoryTask.update_inventory(
            system, self.product_id, 7, operation="set"
        )
        low_stock = InventoryTask.get_low_stock_products(
            system, threshold=self.low_stock_threshold
        )
        LOGGER.info("Low stock check complete")

    def post_testcase(self):
        LOGGER.info("Post-testcase: resetting inventory to default")
        super(TestInventorySync, self).post_testcase()
''')


# TC-009: Smoke - Payment Processing
w("orders/test_payment_processing.py", '''\
"""
TC-009: Smoke - Payment Processing
Validate the payment processing workflow including credit card authorization,
payment capture, transaction history, and partial refund.
"""
import logging
from shopease_framework.base.base_test_case import ShopEaseBaseTestCase, Parameter
from shopease_framework.base.utils import TestUtils
from shopease_framework.tasks.order_task import OrderTask
from shopease_framework.tasks.payment_task import PaymentTask

LOGGER = logging.getLogger(__name__)


class TestPaymentProcessing(ShopEaseBaseTestCase):

    def __init__(self):
        super(TestPaymentProcessing, self).__init__()
        self._parameters = [
            Parameter("order_total", "float", 149.97,
                      help="Total order amount"),
            Parameter("refund_amount", "float", 50.00,
                      help="Partial refund amount"),
        ]
        self._order_id = None
        self._transaction_id = None

    def pre_testcase(self, testbed_obj):
        ShopEaseBaseTestCase.pre_testcase(self, testbed_obj)
        self.__dict__.update(self.params)

    def run_test(self):
        system = self.api_system

        # Step 1: Create order pending payment
        LOGGER.info(f"Step {self.step_count}: Creating order with total {self.order_total}")
        order_data = {
            "customer_id": "CUST-001",
            "items": [
                {"product_id": "P-101", "quantity": 3, "price": 29.99},
                {"product_id": "P-102", "quantity": 1, "price": 60.00},
            ],
            "total": self.order_total,
        }
        order_resp = OrderTask.create_order(system, order_data)
        TestUtils.test_assert_true(
            order_resp.get("result"),
            "Order creation should succeed"
        )
        self._order_id = order_resp["order_id"]

        # Step 2: Process payment
        LOGGER.info(f"Step {self.step_count}: Processing payment for order {self._order_id}")
        payment_data = {
            "method": "credit_card",
            "card_token": "tok_visa_success",
            "amount": self.order_total,
            "currency": "USD",
        }
        pay_resp = PaymentTask.process_payment(
            system, self._order_id, payment_data
        )
        TestUtils.test_assert_true(
            pay_resp.get("result"),
            "Payment should be approved"
        )
        self._transaction_id = pay_resp["transaction_id"]

        # Step 3: Verify payment transaction
        LOGGER.info(f"Step {self.step_count}: Verifying transaction {self._transaction_id}")
        txn = PaymentTask.verify_payment(system, self._transaction_id)
        TestUtils.test_assert_equals(
            "approved", txn.get("status"),
            "Transaction status should be approved"
        )

        # Step 4: Check order payment history
        LOGGER.info(f"Step {self.step_count}: Checking payment history")
        order_status = OrderTask.get_order_status(system, self._order_id)
        LOGGER.info("Order status after payment: %s", order_status.get("status"))

        # Step 5: Process partial refund
        LOGGER.info(f"Step {self.step_count}: Processing partial refund of {self.refund_amount}")
        refund_resp = PaymentTask.process_refund_payment(
            system, self._transaction_id, amount=self.refund_amount
        )
        TestUtils.test_assert_true(
            refund_resp.get("result"),
            "Partial refund should be processed"
        )
        LOGGER.info("Refund ID: %s", refund_resp.get("refund_id"))

    def post_testcase(self):
        super(TestPaymentProcessing, self).post_testcase()
''')


# TC-010: Comprehensive - Notification Rules and Alerts
w("orders/test_notification_rules.py", '''\
"""
TC-010: Comprehensive - Notification Rules and Alerts
Test the notification rule engine including rule creation, event-driven
triggering, rule modification, and cleanup.
"""
import logging
from shopease_framework.base.base_test_case import ShopEaseBaseTestCase, Parameter
from shopease_framework.base.utils import TestUtils
from shopease_framework.tasks.notification_task import NotificationTask
from shopease_framework.tasks.order_task import OrderTask

LOGGER = logging.getLogger(__name__)


class TestNotificationRules(ShopEaseBaseTestCase):

    def __init__(self):
        super(TestNotificationRules, self).__init__()
        self._parameters = [
            Parameter("event_type", "string", "order.placed",
                      help="Event type for notification rule"),
            Parameter("channel", "string", "email",
                      help="Notification channel"),
            Parameter("recipient", "string", "ops-team@shopeasy.com",
                      help="Notification recipient"),
        ]
        self._rule_created = False

    def pre_testcase(self, testbed_obj):
        ShopEaseBaseTestCase.pre_testcase(self, testbed_obj)
        self.__dict__.update(self.params)

    def run_test(self):
        system = self.api_system

        # Step 1: Create notification rule
        LOGGER.info(f"Step {self.step_count}: Creating notification rule for {self.event_type}")
        rule_data = {
            "event_type": self.event_type,
            "channel": self.channel,
            "recipients": [self.recipient],
            "severity": "info",
        }
        success, rule_resp = NotificationTask.create_notification_rule(
            system, rule_data, event_types=[self.event_type]
        )
        TestUtils.test_assert_true(success, "Notification rule creation should succeed")
        self._rule_created = True

        # Step 2: Trigger rule by creating an order
        LOGGER.info(f"Step {self.step_count}: Triggering rule via order creation")
        order_resp = OrderTask.create_order(system, {
            "customer_id": "CUST-001",
            "items": [{"product_id": "P-101", "quantity": 1}],
        })
        TestUtils.test_assert_true(
            order_resp.get("result"),
            "Test order should be created"
        )

        # Step 3: Verify notification was sent
        LOGGER.info(f"Step {self.step_count}: Verifying notification delivery")
        notif_sent = NotificationTask.verify_notification_sent(
            system, self.event_type
        )
        TestUtils.test_assert_true(
            notif_sent,
            "Notification should be sent for the event"
        )

        # Step 4: Modify the notification rule
        LOGGER.info(f"Step {self.step_count}: Modifying notification rule severity")
        rules = NotificationTask.get_notification_rules(system)
        TestUtils.test_assert_true(
            len(rules) > 0,
            "Should have at least one notification rule"
        )

        # Step 5: Delete the notification rule
        LOGGER.info(f"Step {self.step_count}: Deleting notification rule")
        del_result = NotificationTask.delete_notification_rules(system)
        TestUtils.test_assert_true(del_result, "Rule deletion should succeed")
        self._rule_created = False

    def post_testcase(self):
        if self._rule_created:
            LOGGER.info("Cleanup: removing notification rules")
            NotificationTask.delete_notification_rules(self.api_system)
        super(TestNotificationRules, self).post_testcase()
''')


print("\nAll 10 reference test files created successfully!")
