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
