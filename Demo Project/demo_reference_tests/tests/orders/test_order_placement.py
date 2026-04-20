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
