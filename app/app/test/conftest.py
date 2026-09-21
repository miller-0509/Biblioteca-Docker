import os
from datetime import datetime, timedelta

import pytest

from app import create_app, db

TEST_DIR = os.path.dirname(__file__)
APP_DIR = os.path.dirname(TEST_DIR)
STATIC_IMG = os.path.join(APP_DIR, 'static', 'img')


@pytest.fixture(scope='session', autouse=True)
def ensure_sena_logo():
    """Asegura que exista static/img/sena.png, el logo que se incrusta en los QR."""
    from PIL import Image
    logo_path = os.path.join(STATIC_IMG, 'sena.png')
    if not os.path.exists(logo_path):
        os.makedirs(STATIC_IMG, exist_ok=True)
        Image.new('RGB', (50, 50), 'green').save(logo_path)
    yield


@pytest.fixture
def app():
    app = create_app()
    with app.app_context():
        db.create_all()  # Create tables within the context
        yield app
        db.session.remove()  # Cleanup session objects
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user(app):
    from app.models.users import User
    user = User(nameUser="test_user", passwordUser="test_password")
    db.session.add(user)
    db.session.commit()
    yield user


@pytest.fixture
def author(app):
    from app.models.authors import Author
    author = Author(nameAuthor="Gabriel Garcia Marquez", nationalityAuthor="Colombiana")
    db.session.add(author)
    db.session.commit()
    yield author


@pytest.fixture
def book(app, author):
    from app.models.books import Book
    book = Book(titleBook="Cien anios de soledad", authorId=author.idAuthor)
    db.session.add(book)
    db.session.commit()
    yield book


@pytest.fixture
def computer(app):
    from app.models.computers import Computer
    computer = Computer(brandComputer="Dell", modelComputer="OptiPlex 7000", statusComputer="Active")
    db.session.add(computer)
    db.session.commit()
    yield computer


@pytest.fixture
def room(app):
    from app.models.rooms import Room
    room = Room(name="Sala de Estudio", description="Sala silenciosa para estudio")
    db.session.add(room)
    db.session.commit()
    yield room


@pytest.fixture
def loan(app, book, user):
    from app.models.loans import Loan
    loan = Loan(bookId=book.idBook, userId=user.idUser, returnDate=datetime.now() + timedelta(days=14))
    db.session.add(loan)
    db.session.commit()
    yield loan


@pytest.fixture
def cloan(app, computer, user):
    from app.models.cloans import ComputerLoan
    cloan = ComputerLoan(computerId=computer.idComputer, userId=user.idUser,
                         returnDate=datetime.now() + timedelta(days=7))
    db.session.add(cloan)
    db.session.commit()
    yield cloan