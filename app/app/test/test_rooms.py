from app import db
from app.models.rooms import Room


def test_index(client, room):
    response = client.get('/room/')
    assert response.status_code == 200
    assert b"Lista de Salas" in response.data
    assert b"Sala de Estudio" in response.data


def test_add_room(client):
    response = client.post('/room/add', data={
        'name': 'Laboratorio de Sistemas',
        'description': 'Sala con 20 computadores'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Laboratorio de Sistemas" in response.data


def test_edit_room(client, room):
    response = client.post(f'/room/edit/{room.id}', data={
        'name': 'Sala de Estudio Renovada',
        'description': 'Nueva descripcion'
    }, follow_redirects=True)
    assert response.status_code == 200

    room = db.session.get(Room, room.id)
    assert room.name == 'Sala de Estudio Renovada'


def test_delete_room(client, room):
    # La plantilla envía el borrado por POST
    response = client.post(f'/room/delete/{room.id}', follow_redirects=True)
    assert response.status_code == 200
    assert db.session.get(Room, room.id) is None


def test_edit_room_not_found(client):
    response = client.get('/room/edit/999')
    assert response.status_code == 404


def test_delete_room_not_found(client):
    response = client.get('/room/delete/999')
    assert response.status_code == 404