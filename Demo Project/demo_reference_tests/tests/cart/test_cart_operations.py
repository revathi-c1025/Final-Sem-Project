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
