from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_create_group_and_list_groups():
    create_response = client.post('/groups', json={'name': 'Weekend Trip'})
    assert create_response.status_code == 201
    created_group = create_response.json()
    assert created_group['name'] == 'Weekend Trip'
    assert 'id' in created_group

    list_response = client.get('/groups')
    assert list_response.status_code == 200
    assert any(group['id'] == created_group['id'] for group in list_response.json())


def test_add_member_to_group():
    group_response = client.post('/groups', json={'name': 'Family Trip'})
    group_id = group_response.json()['id']

    response = client.post(f'/groups/{group_id}/members', json={'name': 'Alice'})
    assert response.status_code == 201
    member = response.json()
    assert member['name'] == 'Alice'
    assert member['group_id'] == group_id

    list_response = client.get(f'/groups/{group_id}/members')
    assert list_response.status_code == 200
    assert any(item['id'] == member['id'] for item in list_response.json())


def test_add_equal_split_expense_and_get_balances():
    group_response = client.post('/groups', json={'name': 'Office Lunch'})
    group_id = group_response.json()['id']

    member_a = client.post(f'/groups/{group_id}/members', json={'name': 'Alice'}).json()
    member_b = client.post(f'/groups/{group_id}/members', json={'name': 'Bob'}).json()

    expense_response = client.post(
        f'/groups/{group_id}/expenses',
        json={
            'description': 'Groceries',
            'amount': 120,
            'payer_id': member_a['id'],
            'split_type': 'equal',
            'participant_ids': [member_a['id'], member_b['id']],
            'date': '2026-09-11',
        },
    )

    assert expense_response.status_code == 201
    expense = expense_response.json()
    assert expense['description'] == 'Groceries'

    balance_response = client.get(f'/groups/{group_id}/balances')
    assert balance_response.status_code == 200
    balances = balance_response.json()
    assert len(balances) == 2

    balance_map = {item['member_id']: item['balance'] for item in balances}
    assert balance_map[member_a['id']] == 60.0
    assert balance_map[member_b['id']] == -60.0


def test_add_custom_split_expense():
    group_response = client.post('/groups', json={'name': 'Dinner'})
    group_id = group_response.json()['id']

    alice = client.post(f'/groups/{group_id}/members', json={'name': 'Alice'}).json()
    bob = client.post(f'/groups/{group_id}/members', json={'name': 'Bob'}).json()

    response = client.post(
        f'/groups/{group_id}/expenses',
        json={
            'description': 'Dinner bill',
            'amount': 100,
            'payer_id': alice['id'],
            'split_type': 'custom',
            'participant_ids': [alice['id'], bob['id']],
            'custom_shares': {alice['id']: 30, bob['id']: 70},
            'date': '2026-09-12',
        },
    )

    assert response.status_code == 201

    balance_response = client.get(f'/groups/{group_id}/balances')
    balances = {item['member_id']: item['balance'] for item in balance_response.json()}
    assert balances[alice['id']] == 70.0
    assert balances[bob['id']] == -70.0
