import io

import pytest

from app.models.users import User

try:
    from pyzbar.pyzbar import decode
    HAS_PYZBAR = True
except ImportError:
    HAS_PYZBAR = False


def test_index(client):
    response = client.get('/User/')
    assert response.status_code == 200
    assert b"Usuarios" in response.data  # Asumiendo que hay un texto "Users" en la página


def test_add_user(client):
    response = client.post('/User/add', data={
        'nameUser': 'new_user',
        'passwordUser': 'new_password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Usuarios" in response.data  # Asumiendo que el nombre del usuario se muestra en la página


def test_edit_user(client, user):
    response = client.post(f'/User/edit/{user.idUser}', data={
        'nameUser': 'updated_user',
        'passwordUser': 'updated_password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"updated_user" in response.data  # Asumiendo que el nombre del usuario actualizado se muestra en la página


def test_delete_user(client, user):
    response = client.get(f'/User/delete/{user.idUser}', follow_redirects=True)
    assert response.status_code == 200
    assert b"Usuarios" in response.data  # Asumiendo que hay un mensaje de confirmación de eliminación


def test_add_user_duplicate_name(client, user):
    # nameUser es unique=True; insertar uno repetido lanza IntegrityError sin manejar
    response = client.post('/User/add', data={
        'nameUser': user.nameUser,
        'passwordUser': 'otra_password'
    }, follow_redirects=True)
    # BUG CONOCIDO: la app no captura la excepción y devuelve 500
    assert response.status_code == 500


def test_add_user_missing_field(client):
    # Faltan campos obligatorios => Werkzeug devuelve 400 (BadRequestKeyError)
    response = client.post('/User/add', data={
        'nameUser': 'sin_password'
    }, follow_redirects=True)
    assert response.status_code == 400


def test_detail(client, user):
    response = client.get(f'/User/detail/{user.idUser}')
    assert response.status_code == 200
    assert b"Detalle del Usuario" in response.data
    assert b"test_user" in response.data


def test_detail_not_found(client):
    response = client.get('/User/detail/999')
    assert response.status_code == 404


def test_generate_qr(client, user):
    response = client.get(f'/User/qr/{user.idUser}')
    assert response.status_code == 200
    assert response.content_type == 'image/png'
    # La imagen PNG comienza con la firma \x89PNG
    assert response.data.startswith(b'\x89PNG')


def test_generate_qr_not_found(client):
    response = client.get('/User/qr/999')
    assert response.status_code == 404


@pytest.mark.skipif(not HAS_PYZBAR, reason="pyzbar no esta instalado")
def test_read_qr_without_image(client):
    response = client.post('/User/read_qr')
    assert response.status_code == 400
    assert b"No se ha proporcionado una imagen de QR" in response.data


@pytest.mark.skipif(not HAS_PYZBAR, reason="pyzbar no esta instalado")
def test_read_qr_invalid_image(client):
    # Una imagen PNG sin QR: el decodificador no encuentra nada
    from PIL import Image
    img = Image.new('RGB', (10, 10), 'white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    response = client.post('/User/read_qr', data={
        'qr_image': (buf, 'qr.png')
    }, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b"No se pudo leer el c" in response.data


@pytest.mark.skipif(not HAS_PYZBAR, reason="pyzbar no esta instalado")
def test_read_qr_valid(client, user):
    # Generar un QR válido con el ID del usuario
    import json
    import qrcode
    qr_img = qrcode.make(json.dumps({'ID': user.idUser, 'Name': user.nameUser}))
    buf = io.BytesIO()
    qr_img.save(buf, format='PNG')
    buf.seek(0)

    response = client.post('/User/read_qr', data={
        'qr_image': (buf, 'qr.png')
    }, content_type='multipart/form-data')
    assert response.status_code == 200
    assert b"Detalle del Usuario" in response.data
    assert b"test_user" in response.data


@pytest.mark.skipif(not HAS_PYZBAR, reason="pyzbar no esta instalado")
def test_read_qr_user_not_found(client):
    import json
    import qrcode
    qr_img = qrcode.make(json.dumps({'ID': 999, 'Name': 'fantasma'}))
    buf = io.BytesIO()
    qr_img.save(buf, format='PNG')
    buf.seek(0)

    response = client.post('/User/read_qr', data={
        'qr_image': (buf, 'qr.png')
    }, content_type='multipart/form-data')
    assert response.status_code == 404
    assert b"Usuario no encontrado" in response.data


@pytest.mark.skipif(not HAS_PYZBAR, reason="pyzbar no esta instalado")
def test_read_qr_missing_id(client, user):
    import json
    import qrcode
    qr_img = qrcode.make(json.dumps({'Name': 'sin id'}))
    buf = io.BytesIO()
    qr_img.save(buf, format='PNG')
    buf.seek(0)

    response = client.post('/User/read_qr', data={
        'qr_image': (buf, 'qr.png')
    }, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b"No contiene un ID de usuario" in response.data