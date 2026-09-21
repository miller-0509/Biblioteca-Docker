from datetime import datetime

from app import db
from app.models.cloans import ComputerLoan


def test_index(client, cloan):
    response = client.get('/cloans/')
    assert response.status_code == 200
    assert b"Lista de Pr" in response.data


def test_add_cloan(client, computer, user):
    response = client.post('/cloans/add', data={
        'computerId': str(computer.idComputer),
        'userId': str(user.idUser)
    }, follow_redirects=True)
    assert response.status_code == 200

    loan = ComputerLoan.query.first()
    assert loan is not None
    assert loan.status == 'Active'
    assert loan.computerId == computer.idComputer
    assert loan.userId == user.idUser


def test_edit_cloan(client, cloan, computer, user):
    loan_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    response = client.post(f'/cloans/update/{cloan.idLoan}', data={
        'computerId': str(computer.idComputer),
        'userId': str(user.idUser),
        'loanDate': loan_date,
        'returnDate': loan_date,
        'status': 'Returned'
    }, follow_redirects=True)
    assert response.status_code == 200

    loan = db.session.get(ComputerLoan, cloan.idLoan)
    assert loan.status == 'Returned'
    assert loan.computerId == computer.idComputer


def test_delete_cloan(client, cloan):
    response = client.post(f'/cloans/delete/{cloan.idLoan}', follow_redirects=True)
    assert response.status_code == 200
    assert db.session.get(ComputerLoan, cloan.idLoan) is None


def test_delete_cloan_wrong_method(client, cloan):
    # La ruta de borrado solo acepta POST
    response = client.get(f'/cloans/delete/{cloan.idLoan}')
    assert response.status_code == 405


def test_delete_cloan_not_found(client):
    response = client.post('/cloans/delete/999', follow_redirects=True)
    assert response.status_code == 404


def test_return_cloan_wrong_method(client, cloan):
    # La ruta de devolución solo acepta POST
    response = client.get(f'/cloans/return/{cloan.idLoan}')
    assert response.status_code == 405


def test_return_cloan_not_found(client):
    response = client.post('/cloans/return/999', follow_redirects=True)
    assert response.status_code == 404


def test_return_cloan(client, cloan):
    response = client.post(f'/cloans/return/{cloan.idLoan}', follow_redirects=True)
    assert response.status_code == 200

    loan = db.session.get(ComputerLoan, cloan.idLoan)
    assert loan.status == 'Returned'
    assert loan.returnDate is not None


def test_edit_cloan_not_found(client):
    response = client.get('/cloans/update/999')
    assert response.status_code == 404