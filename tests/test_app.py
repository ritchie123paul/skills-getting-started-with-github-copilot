import copy
from fastapi.testclient import TestClient

from src.app import app, activities


import pytest


@pytest.fixture
def client():
    # snapshot activities and restore after each test to keep tests isolated
    original = copy.deepcopy(activities)
    with TestClient(app) as c:
        yield c
    activities.clear()
    activities.update(original)


def test_get_activities(client):
    res = client.get('/activities')
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    # Expect at least one known activity
    assert 'Tennis Club' in data


def test_signup_and_unregister_flow(client):
    activity = 'Tennis Club'
    email = 'test.user@example.com'

    # Ensure email not already present
    before = client.get('/activities').json()
    assert email not in before[activity]['participants']

    # Sign up
    res = client.post(f"/activities/{activity}/signup", params={'email': email})
    assert res.status_code == 200
    assert 'Signed up' in res.json().get('message', '')

    # Verify participant appears
    after = client.get('/activities').json()
    assert email in after[activity]['participants']

    # Unregister
    res2 = client.delete(f"/activities/{activity}/unregister", params={'email': email})
    assert res2.status_code == 200
    assert 'Unregistered' in res2.json().get('message', '')

    # Verify removal
    final = client.get('/activities').json()
    assert email not in final[activity]['participants']
