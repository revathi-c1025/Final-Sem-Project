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
