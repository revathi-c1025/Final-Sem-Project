"""Base test case for ShopEasy E-Commerce API test automation."""

import logging
import time

LOGGER = logging.getLogger(__name__)


class Parameter:
    """Test parameter definition."""
    def __init__(self, name, param_type="string", default=None, required=False, help=""):
        self.name = name
        self.param_type = param_type
        self.default = default
        self.required = required
        self.help = help


class ShopEaseBaseTestCase:
    """
    Base class for all ShopEasy E-Commerce test cases.

    Provides:
    - API connection setup via pre_testcase
    - self.api_system (API connection object after pre_testcase)
    - Parameter management via self._parameters and self.params
    - Test step counting via self._step_count / self.step_count
    """

    _skip_pre_testcase_dump_check = False

    def __init__(self):
        self._parameters = []
        self.params = {}
        self._step_count = 0
        self.api_system = None
        self._start_time = None

    @property
    def step_count(self):
        self._step_count += 1
        return self._step_count

    def pre_testcase(self, testbed_obj):
        """Setup test environment. Called before run_test."""
        LOGGER.info("Setting up test environment from testbed")
        self._start_time = time.time()
        self.params = {}
        for param in self._parameters:
            self.params[param.name] = param.default
        if testbed_obj and "api_system" in testbed_obj:
            self.api_system = testbed_obj["api_system"]
        LOGGER.info("Test environment setup complete")

    def run_test(self):
        """Override in subclass to implement test steps."""
        raise NotImplementedError("Subclasses must implement run_test()")

    def post_testcase(self):
        """Cleanup after test. Override in subclass."""
        elapsed = time.time() - self._start_time if self._start_time else 0
        LOGGER.info("Test completed in %.2f seconds", elapsed)

    def get_products_from_testbed(self, testbed_obj, product_count=1, product_names=None):
        """Get test products from testbed configuration."""
        if product_names is None:
            product_names = ["product_1"]
        products = testbed_obj.get("PRODUCTS", {})
        result = {"PRODUCTS": [], "CATEGORIES": [], "WAREHOUSES": []}
        for name in product_names[:product_count]:
            if name in products:
                result["PRODUCTS"].append(products[name])
        if "CATEGORIES" in testbed_obj:
            result["CATEGORIES"] = testbed_obj["CATEGORIES"]
        if "WAREHOUSES" in testbed_obj:
            result["WAREHOUSES"] = testbed_obj["WAREHOUSES"]
        return result

    def sync_product_catalog(self, testbed_obj=None, system=None, product_names=None):
        """Sync product catalog with the API system."""
        LOGGER.info("Syncing product catalog with API system")
        if product_names is None:
            product_names = ["product_1"]
        product_ids = {}
        for name in product_names:
            product_ids[name] = f"PROD-{hash(name) % 10000:04d}"
        return True, {}, product_ids
