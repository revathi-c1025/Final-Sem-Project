"""Category management tasks."""
import logging
LOGGER = logging.getLogger(__name__)

class CategoryTask:
    @staticmethod
    def create_category(system, category_name, parent_id=None):
        LOGGER.info("Creating category: %s", category_name)
        return {"result": True, "category_id": 501, "category_name": category_name}
    @staticmethod
    def verify_category(system, create_category_response):
        return True
    @staticmethod
    def add_verify_products_in_category(system, category_ids, product_ids):
        return True
    @staticmethod
    def get_all_categories(system):
        return [{"id": 501, "name": "Electronics"}, {"id": 502, "name": "Clothing"}]
    @staticmethod
    def delete_categories(system, category_name=None, category_id=None):
        return True
