def test_index(client, author):
    response = client.get('/Author/')
    assert response.status_code == 200
    assert b"Lista de Autores" in response.data
    assert b"Gabriel Garcia Marquez" in response.data


def test_list_books_of_author(client, author, book):
    response = client.get(f'/Author/list/{author.idAuthor}')
    assert response.status_code == 200
    assert b"Lista de Libros" in response.data
    assert b"Cien anios de soledad" in response.data


def test_add_author(client):
    response = client.post('/Author/add', data={
        'nameAuthor': 'Mario Vargas Llosa',
        'nationalityAuthor': 'Peruana'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Mario Vargas Llosa" in response.data


def test_edit_author(client, author):
    response = client.post(f'/Author/edit/{author.idAuthor}', data={
        'nameAuthor': 'Gabriel Garcia Marquez Editado',
        'nationalityAuthor': 'Mexicana'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Editado" in response.data


def test_delete_author(client, author):
    response = client.get(f'/Author/delete/{author.idAuthor}', follow_redirects=True)
    assert response.status_code == 200
    assert b"Lista de Autores" in response.data


def test_edit_author_not_found(client):
    response = client.get('/Author/edit/999')
    assert response.status_code == 404


def test_delete_author_not_found(client):
    response = client.get('/Author/delete/999')
    assert response.status_code == 404