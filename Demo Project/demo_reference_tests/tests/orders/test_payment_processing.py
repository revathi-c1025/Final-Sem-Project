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
