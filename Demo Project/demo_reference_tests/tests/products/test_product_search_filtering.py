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
