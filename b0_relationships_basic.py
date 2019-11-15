from uuid import uuid4

from flask import Flask, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql

app = Flask(__name__)  # Create Flask App
# postgresql://user@pass:host/db
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test:test@localhost/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class MySQLAlchemy(SQLAlchemy):
    UUID = postgresql.UUID  # Add psql's UUID type
    CASCADE_DEL = 'all, delete-orphan'


db = MySQLAlchemy(app, session_options={'autoflush': False})


class Computer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.Unicode, nullable=False)
    manufacturer = db.Column(db.Unicode, nullable=False)
    serial_number = db.Column(db.Unicode, nullable=False)
    author_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    author = db.relationship(lambda: User,
                             backref=db.backref('computers',
                                                lazy=True,
                                                cascade=db.CASCADE_DEL,
                                                order_by=lambda: Computer.id,
                                                collection_class=set),
                             primaryjoin=lambda: User.id == Computer.author_id)
    # Lazy loading: emitting additional SQL queries when accessing the attribute

    __table_args__ = (
        db.Index('model_index', model),
        db.Index('author_index', author_id, postgresql_using='hash'),
    )

    def __repr__(self) -> str:
        return f'<Computer {self.id} model={self.model} S/N={self.serial_number}>'


class User(db.Model):
    """The user class.

    :attr computers: The computers the user created.
    """
    id = db.Column(db.UUID(as_uuid=True), default=uuid4, primary_key=True)
    email = db.Column(db.Unicode, nullable=False, unique=True)

    # computers = relationship to Computer through Computer's backref

    def __repr__(self) -> str:
        return f'<User {self.id} {self.email}. PCs={self.computers}>'


db.drop_all()
db.create_all()


@app.route('/users/', methods={'POST'})
def add_user():
    """Creates an user."""
    user = User(email='foo@bar.com')
    db.session.add(user)
    db.session.flush()
    r = make_response(str(user))
    db.session.commit()
    return r


@app.route('/pcs/', methods={'POST'})
def hello_world():
    """Creates a PC, adding it to the database and returning it.

    The author of this PC is set to the first user created.
    """
    pc = Computer(model='foo', manufacturer='bar', serial_number='123')
    user = User.query.first()  # Get the first user created

    # The relationship magic happens HERE!
    # Note that user.computers starts defined as an empty set
    # DON'T DO user.computers = set()
    user.computers.add(pc)

    # Note that we don't have to explicitly add the computer to session
    # It is added when you relate it to an existing object or an object
    # that was already added to the session
    db.session.flush()
    r = make_response(str(user))
    db.session.commit()
    return r


@app.route('/users/')
def get_users():
    """GETs the first user."""
    user = User.query.first()
    return make_response(str(user))


@app.route('/pcs/<email>')
def get_devices_from_email(email):
    """GETs the computers authored by the passed-in email."""
    pcs = Computer.query.join(Computer.author).filter(User.email == email)
    return make_response(f'The user with email {email} has computers: {tuple(pcs)}')


# Tests
client = app.test_client()
print('Create one user:')
print('Response:', client.post('/users/').data)

print('Create one PC authored by the user:')
print('Response:', client.post('/pcs/').data)

print('Get users:')
print('Response:', client.get('/users/').data)

print('Get the device of a specific user:')
print('Response:', client.get('/pcs/foo@bar.com').data)
