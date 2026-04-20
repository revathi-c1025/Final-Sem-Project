"""Order API service layer."""
import logging
LOGGER = logging.getLogger(__name__)

class OrderService:
    @staticmethod
    def get_order_settings(system, check_return_code=False):
        class Response:
            return_code = 200
            data = [{"value": [
                {"Name": "MAX_ORDER_ITEMS", "Value": "100", "GroupName": "ORDER_SETTINGS"},
                {"Name": "AUTO_CANCEL_HOURS", "Value": "24", "GroupName": "ORDER_SETTINGS"},
                {"Name": "PAYMENT_TIMEOUT", "Value": "300", "GroupName": "PAYMENT_SETTINGS"},
            ]}]
        return Response()
    @staticmethod
    def update_order_settings(system, group_name="", name="", value="", **kwargs):
        class Response:
            return_code = 201
        return Response()
