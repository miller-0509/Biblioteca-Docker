from datetime import datetime, timedelta

from app import db
from app.models.loans import Loan


def test_index(client, loan):
    response = client.get('/Loan/')
    assert response.status_code == 200
    assert b"Lista de Pr" in response.data


def test_add_loan(client, book, user):
    response = client.post('/Loan/add', data={
        'bookId': str(book.idBook),
        'userId': str(user.idUser)
    }, follow_redirects=True)
    assert response.status_code == 200

    loan = Loan.query.first()
    assert loan is not None
    assert loan.status == 'Active'
    assert loan.fine == 0.0
    assert loan.bookId == book.idBook
    assert loan.userId == user.idUser


def test_edit_loan(client, loan):
    new_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    response = client.post(f'/Loan/edit/{loan.idLoan}', data={
        'returnDate': new_date,
        'fine': '10.5',
        'status': 'Overdue'
    }, follow_redirects=True)
    assert response.status_code == 200

    loan = db.session.get(Loan, loan.idLoan)
    assert loan.fine == 10.5
    assert loan.status == 'Overdue'


def test_delete_loan(client, loan):
    response = client.get(f'/Loan/delete/{loan.idLoan}', follow_redirects=True)
    assert response.status_code == 200
    assert db.session.get(Loan, loan.idLoan) is None


def test_return_loan_on_time_no_fine(client, loan):
    # Devolución antes de la fecha límite: sin multa
    loan.returnDate = datetime.now() + timedelta(days=1)
    db.session.commit()

    response = client.get(f'/Loan/return/{loan.idLoan}', follow_redirects=True)
    assert response.status_code == 200

    loan = db.session.get(Loan, loan.idLoan)
    assert loan.status == 'Returned'
    assert loan.fine == 0.0


def test_return_loan_late_applies_fine(client, loan):
    # Devolución 5 días después: multa de 1.0 por día => 5.0
    loan.returnDate = datetime.now() - timedelta(days=5)
    loan.fine = 0.0
    db.session.commit()

    response = client.get(f'/Loan/return/{loan.idLoan}', follow_redirects=True)
    assert response.status_code == 200

    loan = db.session.get(Loan, loan.idLoan)
    assert loan.status == 'Returned'
    assert loan.fine == 5.0


def test_edit_loan_not_found(client):
    response = client.get('/Loan/edit/999')
    assert response.status_code == 404


def test_delete_loan_not_found(client):
    response = client.get('/Loan/delete/999')
    assert response.status_code == 404