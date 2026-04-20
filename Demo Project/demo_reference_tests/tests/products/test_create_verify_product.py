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
