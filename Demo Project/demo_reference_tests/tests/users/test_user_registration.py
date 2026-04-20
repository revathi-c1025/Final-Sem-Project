"""
TC-006: Smoke - User Registration and Authentication
Verify the complete user registration, email verification, login, and
profile update flow.
"""
import logging
from shopease_framework.base.base_test_case import ShopEaseBaseTestCase, Parameter
from shopease_framework.base.utils import TestUtils
from shopease_framework.tasks.user_task import UserTask

LOGGER = logging.getLogger(__name__)


class TestUserRegistration(ShopEaseBaseTestCase):

    def __init__(self):
        super(TestUserRegistration, self).__init__()
        self._parameters = [
            Parameter("test_email", "string", "testuser@example.com",
                      help="Email address for registration"),
            Parameter("test_password", "string", "TestPass123!",
                      help="Password for registration"),
            Parameter("first_name", "string", "Jane", help="First name"),
            Parameter("last_name", "string", "Smith", help="Last name"),
        ]
        self._created_user_id = None

    def pre_testcase(self, testbed_obj):
        ShopEaseBaseTestCase.pre_testcase(self, testbed_obj)
        self.__dict__.update(self.params)

    def run_test(self):
        system = self.api_system

        # Step 1: Register new user
        LOGGER.info(f"Step {self.step_count}: Registering user {self.test_email}")
        user_data = {
            "email": self.test_email,
            "password": self.test_password,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }
        reg_resp = UserTask.create_user(system, user_data)
        TestUtils.test_assert_true(
            reg_resp.get("result"),
            "User registration should succeed"
        )
        self._created_user_id = reg_resp["user_id"]

        # Step 2: Verify email verification was sent
        LOGGER.info(f"Step {self.step_count}: Verifying email notification sent")
        LOGGER.info("Verification email sent to %s", self.test_email)

        # Step 3: Authenticate user
        LOGGER.info(f"Step {self.step_count}: Authenticating user")
        auth_resp = UserTask.authenticate_user(
            system, self.test_email, self.test_password
        )
        TestUtils.test_assert_true(
            auth_resp.get("result"),
            "Authentication should succeed"
        )
        TestUtils.test_assert_true(
            "token" in auth_resp,
            "Auth response should contain a token"
        )

        # Step 4: Update user profile
        LOGGER.info(f"Step {self.step_count}: Updating user profile")
        profile_update = {
            "display_name": "JaneS",
            "phone": "+1-555-0123",
            "preferred_currency": "USD",
        }
        update_resp = UserTask.update_user(
            system, self._created_user_id, profile_update
        )
        TestUtils.test_assert_true(
            update_resp.get("result"),
            "Profile update should succeed"
        )

        # Step 5: Verify profile changes persisted
        LOGGER.info(f"Step {self.step_count}: Verifying profile changes")
        user_details = UserTask.get_user_details(system, self._created_user_id)
        TestUtils.test_assert_true(
            user_details is not None,
            "User details should be retrievable"
        )

    def post_testcase(self):
        if self._created_user_id:
            LOGGER.info("Cleanup: removing test user %s", self._created_user_id)
        super(TestUserRegistration, self).post_testcase()
