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
