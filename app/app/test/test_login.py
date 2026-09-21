def test_login_success(client, user):
    # Enviar una solicitud POST con las credenciales correctas
    response = client.post('/', data={
        'nameUser': user.nameUser,
        'passwordUser': user.passwordUser
    }, follow_redirects=True)

    # El login redirige al índice de usuarios (/User/)
    assert response.status_code == 200
    assert b"Lista de Usuarios" in response.data


def test_login_redirects_to_user_index(client, user):
    # Sin seguir la redirección: debe ser 302 hacia /User/
    response = client.post('/', data={
        'nameUser': user.nameUser,
        'passwordUser': user.passwordUser
    })
    assert response.status_code == 302
    assert response.headers['Location'] == '/User/'


def test_login_invalid_credentials(client):
    # Enviar una solicitud POST con credenciales incorrectas
    response = client.post('/', data={
        'nameUser': 'wronguser',
        'passwordUser': 'wrongskdfghgpassword'
    }, follow_redirects=True)

    # Verificar que el login fue rechazado
    assert response.status_code == 200
    assert b"Invalid credentials. Please try again." in response.data


def test_login_user_exists_wrong_password(client, user):
    # Usuario correcto pero contraseña equivocada
    response = client.post('/', data={
        'nameUser': user.nameUser,
        'passwordUser': 'contraseña-incorrecta'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid credentials. Please try again." in response.data
    assert b"Lista de Usuarios" not in response.data


# test_auth.py
def test_login_already_authenticated(client, user):
    # Simular un usuario autenticado
    with client:
        with client.session_transaction() as session:
            # Simula que el usuario está autenticado
            session['_user_id'] = str(user.idUser)

        # El usuario ya autenticado debería ser redirigido al dashboard
        response = client.get('/dashboard', follow_redirects=True)
        assert response.status_code == 200
        assert b"This is your dashboard" in response.data


def test_dashboard_requires_login(client):
    # Sin sesión, /dashboard debe redirigir al login
    response = client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b"Iniciar sesi" in response.data


def test_logout(client, user):
    # Iniciar sesión primero
    client.post('/', data={
        'nameUser': user.nameUser,
        'passwordUser': user.passwordUser
    })

    # Cerrar sesión redirige al login
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Iniciar sesi" in response.data