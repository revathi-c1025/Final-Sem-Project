"""
Standalone Test Framework - Replaces Atlas Framework
Simple pytest-based framework for demo purposes.
"""

import pytest
import logging
from typing import Any, Dict, Optional


class BaseTestCase:
    """
    Base test case class for standalone test framework.
    Replaces ShopEasyBaseTestCase from Atlas framework.
    """

    def setup_method(self):
        """Setup method called before each test."""
        self.test_data = {}
        self.step_count = 0
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Starting test: {self.__class__.__name__}")

    def teardown_method(self):
        """Teardown method called after each test."""
        self.logger.info(f"Completed test: {self.__class__.__name__}")

    @property
    def params(self) -> Dict:
        """Test parameters."""
        return self.test_data

    def increment_step(self):
        """Increment step counter."""
        self.step_count += 1
        return self.step_count

    def log_step(self, message: str):
        """Log a test step."""
        step = self.increment_step()
        self.logger.info(f"Step {step}: {message}")
        return step


class TestAssertions:
    """
    Assertion utilities for test framework.
    Replaces TestUtils from Atlas framework.
    """

    @staticmethod
    def assert_equals(expected: Any, actual: Any, message: str = ""):
        """Assert that two values are equal."""
        assert expected == actual, f"{message}: Expected {expected}, got {actual}"

    @staticmethod
    def assert_true(condition: bool, message: str = ""):
        """Assert that a condition is true."""
        assert condition, f"{message}: Expected True, got {condition}"

    @staticmethod
    def assert_false(condition: bool, message: str = ""):
        """Assert that a condition is false."""
        assert not condition, f"{message}: Expected False, got {condition}"

    @staticmethod
    def assert_contains(haystack: Any, needle: Any, message: str = ""):
        """Assert that haystack contains needle."""
        assert needle in haystack, f"{message}: Expected {haystack} to contain {needle}"

    @staticmethod
    def assert_greater(value: Any, threshold: Any, message: str = ""):
        """Assert that value is greater than threshold."""
        assert value > threshold, f"{message}: Expected {value} > {threshold}"

    @staticmethod
    def assert_less(value: Any, threshold: Any, message: str = ""):
        """Assert that value is less than threshold."""
        assert value < threshold, f"{message}: Expected {value} < {threshold}"

    @staticmethod
    def assert_in_range(value: Any, min_val: Any, max_val: Any, message: str = ""):
        """Assert that value is within range."""
        assert min_val <= value <= max_val, f"{message}: Expected {value} in range [{min_val}, {max_val}]"


class MockAPIClient:
    """
    Mock API client for testing.
    Provides simple interface to the mock ShopEasy API.
    """

    def __init__(self):
        from mock_shopeasy_api import mock_api
        self.api = mock_api

    def create_product(self, product_data: Dict) -> Dict:
        """Create a product."""
        return self.api.create_product(product_data)

    def get_product(self, product_id: int) -> Dict:
        """Get a product."""
        return self.api.get_product(product_id)

    def update_product(self, product_id: int, update_data: Dict) -> Dict:
        """Update a product."""
        return self.api.update_product(product_id, update_data)

    def search_products(self, **kwargs) -> Dict:
        """Search products."""
        return self.api.search_products(**kwargs)

    def create_category(self, category_data: Dict) -> Dict:
        """Create a category."""
        return self.api.create_category(category_data)

    def get_category(self, category_id: int) -> Dict:
        """Get a category."""
        return self.api.get_category(category_id)

    def update_category(self, category_id: int, update_data: Dict) -> Dict:
        """Update a category."""
        return self.api.update_category(category_id, update_data)

    def delete_category(self, category_id: int, **kwargs) -> Dict:
        """Delete a category."""
        return self.api.delete_category(category_id, **kwargs)

    def create_order(self, order_data: Dict) -> Dict:
        """Create an order."""
        return self.api.create_order(order_data)

    def get_order(self, order_id: int) -> Dict:
        """Get an order."""
        return self.api.get_order(order_id)

    def update_order_status(self, order_id: int, status: str, **kwargs) -> Dict:
        """Update order status."""
        return self.api.update_order_status(order_id, status, **kwargs)

    def create_cart(self, user_id: str) -> Dict:
        """Create a cart."""
        return self.api.create_cart(user_id)

    def add_cart_item(self, cart_id: int, product_id: int, quantity: int) -> Dict:
        """Add item to cart."""
        return self.api.add_cart_item(cart_id, product_id, quantity)

    def update_cart_item(self, cart_id: int, product_id: int, quantity: int) -> Dict:
        """Update cart item."""
        return self.api.update_cart_item(cart_id, product_id, quantity)

    def apply_discount(self, cart_id: int, discount_code: str) -> Dict:
        """Apply discount to cart."""
        return self.api.apply_discount(cart_id, discount_code)

    def register_user(self, user_data: Dict) -> Dict:
        """Register a user."""
        return self.api.register_user(user_data)

    def get_user(self, user_id: int) -> Dict:
        """Get a user."""
        return self.api.get_user(user_id)

    def update_user_profile(self, user_id: int, profile_data: Dict) -> Dict:
        """Update user profile."""
        return self.api.update_user_profile(user_id, profile_data)

    def get_notifications(self, **kwargs) -> Dict:
        """Get notifications."""
        return self.api.get_notifications(**kwargs)

    def health_check(self) -> Dict:
        """Health check."""
        return self.api.health_check()


# Convenience functions
def assert_equals(expected: Any, actual: Any, message: str = ""):
    """Assert that two values are equal."""
    TestAssertions.assert_equals(expected, actual, message)


def assert_true(condition: bool, message: str = ""):
    """Assert that a condition is true."""
    TestAssertions.assert_true(condition, message)


def assert_contains(haystack: Any, needle: Any, message: str = ""):
    """Assert that haystack contains needle."""
    TestAssertions.assert_contains(haystack, needle, message)


def assert_greater(value: Any, threshold: Any, message: str = ""):
    """Assert that value is greater than threshold."""
    TestAssertions.assert_greater(value, threshold, message)
