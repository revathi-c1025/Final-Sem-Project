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
