"""Test utility functions for ShopEasy test automation."""

import logging
import time

LOGGER = logging.getLogger(__name__)


class TestUtils:
    """Utility class for common test assertions and operations."""

    @staticmethod
    def test_assert_equals(expected, actual, message=""):
        if expected != actual:
            LOGGER.error("FAIL: %s | Expected: %s | Actual: %s", message, expected, actual)
            raise AssertionError(f"{message}: expected={expected}, actual={actual}")
        LOGGER.info("PASS: %s | Value: %s", message, actual)
        return True

    @staticmethod
    def test_assert_true(condition, message=""):
        if not condition:
            LOGGER.error("FAIL: %s", message)
            raise AssertionError(message)
        LOGGER.info("PASS: %s", message)
        return True

    @staticmethod
    def generate_unique_name(prefix="test"):
        return f"{prefix}_{int(time.time())}"

    @staticmethod
    def wait_for_condition(condition_fn, timeout=60, interval=5, message=""):
        start = time.time()
        while time.time() - start < timeout:
            if condition_fn():
                return True
            time.sleep(interval)
        raise TimeoutError(f"Timed out waiting for: {message}")
