"""Decorators for test reporting and metadata."""

import functools
import logging

LOGGER = logging.getLogger(__name__)


def test_reporter(test_id_name=None, test_name=None):
    """Decorator that registers test metadata for reporting."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper._test_id = test_id_name
        wrapper._test_name = test_name
        return wrapper
    return decorator
