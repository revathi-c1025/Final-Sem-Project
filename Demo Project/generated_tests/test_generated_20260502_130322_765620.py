import os

import pytest
import requests


BASE_URL = os.environ.get('API_BASE_URL', 'http://127.0.0.1:8001')
DEFAULT_TOKEN = os.environ.get('API_TOKEN', '')


def build_url(endpoint):
    if endpoint.startswith('http://') or endpoint.startswith('https://'):
        return endpoint
    return BASE_URL.rstrip('/') + '/' + endpoint.lstrip('/')


def auth_headers(auth_type='Bearer', token_env=None):
    if auth_type == 'None':
        return {}
    token = os.environ.get(token_env, '') if token_env else DEFAULT_TOKEN
    if not token:
        return {}
    if auth_type == 'Basic':
        return {'Authorization': 'Basic ' + token}
    return {'Authorization': 'Bearer ' + token}


@pytest.mark.parametrize('case', [
    {'name': 'step_1_get_products', 'method': 'GET', 'endpoint': '/products', 'expected_status': 200, 'auth_type': 'Bearer', 'token_env': None, 'json': None},
])
def test_generated_api_step(case):
    response = requests.request(
        case['method'],
        build_url(case['endpoint']),
        headers=auth_headers(case['auth_type'], case.get('token_env')),
        json=case.get('json'),
        timeout=15,
    )
    assert response.status_code == case['expected_status']
