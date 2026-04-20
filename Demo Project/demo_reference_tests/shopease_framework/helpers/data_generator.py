"""Test data generation utilities."""
import random
import string

class DataGenerator:
    @staticmethod
    def random_product(category="Electronics"):
        name = f"Test Product {random.randint(1000, 9999)}"
        return {"name": name, "price": round(random.uniform(9.99, 999.99), 2),
                "category": category, "sku": f"SKU-{random.randint(10000, 99999)}"}
    @staticmethod
    def random_user():
        suffix = "".join(random.choices(string.ascii_lowercase, k=6))
        return {"name": f"User {suffix}", "email": f"{suffix}@example.com",
                "password": "TestPass123!"}
    @staticmethod
    def random_address():
        return {"street": "123 Test St", "city": "Testville", "state": "CA",
                "zip": "90210", "country": "US"}
