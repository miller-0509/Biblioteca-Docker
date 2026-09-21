def test_index(client, book):
    response = client.get('/Book/')
    assert response.status_code == 200
    assert b"Lista de Libros" in response.data
    assert b"Cien anios de soledad" in response.data


def test_add_book(client, author):
    response = client.post('/Book/add', data={
        'titleBook': 'La ciudad y los perros',
        'authorId': str(author.idAuthor)
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"La ciudad y los perros" in response.data


def test_edit_book(client, book, author):
    response = client.post(f'/Book/edit/{book.idBook}', data={
        'titleBook': 'Cronica de una muerte anunciada',
        'authorId': str(author.idAuthor)
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Cronica de una muerte anunciada" in response.data


def test_delete_book(client, book):
    response = client.get(f'/Book/delete/{book.idBook}', follow_redirects=True)
    assert response.status_code == 200
    assert b"Lista de Libros" in response.data


def test_edit_book_not_found(client):
    response = client.get('/Book/edit/999')
    assert response.status_code == 404


def test_delete_book_not_found(client):
    response = client.get('/Book/delete/999')
    assert response.status_code == 404