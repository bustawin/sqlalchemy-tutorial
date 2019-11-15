import enum
import ipaddress

import sqlalchemy_utils
from flask import Flask, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import TypeDecorator
from sqlalchemy.dialects import postgresql

app = Flask(__name__)  # Create Flask App
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test:test@localhost/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class IP(TypeDecorator):
    """This is a custom type in SQLAlchemy. It is based on the
    PSQL INET type, converting python ipadress objects to PSQL INET.
    ipaddress support for SQLAlchemy as PSQL INET."""
    impl = postgresql.INET

    # We could override __init__ to pass-in options

    def process_bind_param(self, value, dialect):
        # Executed when the value is being casted to the DB
        # Returns what PSQL expects
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        # Executed when the value is retreived from the DB
        # Returns what the user expects
        if value is None:
            return None
        return ipaddress.ip_address(value)


class MySQLAlchemy(SQLAlchemy):
    Email = sqlalchemy_utils.EmailType
    Password = sqlalchemy_utils.PasswordType
    IP = IP


db = MySQLAlchemy(app, session_options={'autoflush': False})


class Language(enum.Enum):
    # ESP, EN... are stored in PSQL as an "Enumerated Type"
    ESP = 'Spanish'
    EN = 'English'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Email)
    password = db.Column(db.Password(max_length=20, schemes={'pbkdf2_sha256'}))
    receive_newsletter = db.Column(db.Boolean, default=False)
    last_ip = db.Column(db.IP())
    language = db.Column(db.Enum(Language))
    created = db.Column(db.TIMESTAMP(timezone=True),
                        nullable=False,
                        server_default=db.text('CURRENT_TIMESTAMP'))

    # This field returns a datetime object that is correctly manages
    # the timezone (PSQL is timezone naive so this translates it)
    # server_default translates to a "DEFAULT" SQL clause
    # so this value is filled by the DB when it is inserted empty

    def __str__(self) -> str:
        return f'User {self.id} {self.email} {self.last_ip} on {self.created}'


db.drop_all()
db.create_all()


@app.route('/', methods={'POST'})
def create_user():
    """Creates an user with several custom types, and returns it."""
    user = User(email='foo@bar.com',
                password='foo',
                receive_newsletter=True,
                language=Language.ESP,
                last_ip=ipaddress.IPv4Address('192.168.1.1'))

    db.session.add(user)
    db.session.flush()
    r = make_response(str(user))
    db.session.commit()
    return r


client = app.test_client()
print('Create the user with the types:')
print('Response:', client.post('/').data)
