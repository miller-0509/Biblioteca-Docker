from app import db
from app.models.computers import Computer


def test_index(client, computer):
    response = client.get('/computers/')
    assert response.status_code == 200
    assert b"Lista de Computadoras" in response.data
    assert b"OptiPlex 7000" in response.data


def test_add_computer(client):
    response = client.post('/computers/add', data={
        'brandComputer': 'HP',
        'modelComputer': 'ProBook 450',
        'statusComputer': 'Active'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"ProBook 450" in response.data


def test_update_computer(client, computer):
    response = client.post(f'/computers/update/{computer.idComputer}', data={
        'brandComputer': 'Lenovo',
        'modelComputer': 'ThinkPad T14',
        'statusComputer': 'Maintenance'
    }, follow_redirects=True)
    assert response.status_code == 200

    computer = db.session.get(Computer, computer.idComputer)
    assert computer.brandComputer == 'Lenovo'
    assert computer.modelComputer == 'ThinkPad T14'
    assert computer.statusComputer == 'Maintenance'


def test_delete_computer(client, computer):
    response = client.post(f'/computers/delete/{computer.idComputer}', follow_redirects=True)
    assert response.status_code == 200
    assert db.session.get(Computer, computer.idComputer) is None


def test_delete_computer_wrong_method(client, computer):
    # La ruta de borrado solo acepta POST
    response = client.get(f'/computers/delete/{computer.idComputer}')
    assert response.status_code == 405


def test_delete_computer_not_found(client):
    response = client.post('/computers/delete/999', follow_redirects=True)
    assert response.status_code == 404


def test_update_computer_not_found(client):
    response = client.get('/computers/update/999')
    assert response.status_code == 404