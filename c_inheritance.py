from flask import Flask, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declared_attr

app = Flask(__name__)  # Create Flask App
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test:test@localhost/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class MySQLAlchemy(SQLAlchemy):
    UUID = postgresql.UUID  # Add psql's UUID type
    CASCADE_DEL = 'save-update, merge, delete-orphan'


db = MySQLAlchemy(app, session_options={'autoflush': False})


class Computer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Unicode(), nullable=False)
    model = db.Column(db.Unicode)
    manufacturer = db.Column(db.Unicode)
    serial_number = db.Column(db.Unicode)

    def __str__(self) -> str:
        return f'Computer {self.id} S/N {self.serial_number}'

    def __repr__(self) -> str:
        return str(self)

    @declared_attr
    def __mapper_args__(cls):
        """Defines inheritance.

        From `the guide <http://docs.sqlalchemy.org/en/latest/orm/
        extensions/declarative/api.html
        #sqlalchemy.ext.declarative.declared_attr>`_
        """
        # This method is only set up in the base class
        # This + Desktop.id creates a "Join Table inheritance"
        args = {'polymorphic_identity': cls.__name__}
        if cls.__name__ == 'Computer':
            # The attribute type is a string that automatically stores
            # the name of the subclass the object is (i.e. "Desktop" / "Laptop")
            args['polymorphic_on'] = cls.type
        return args


class Desktop(Computer):
    id = db.Column(db.Integer, db.ForeignKey(Computer.id), primary_key=True)
    internal_lightning = db.Column(db.Boolean)

    def __str__(self) -> str:
        return f'Desktop {self.id} S/N {self.serial_number}'


class Laptop(Computer):
    id = db.Column(db.Integer, db.ForeignKey(Computer.id), primary_key=True)
    keyboard_layout = db.Column(db.Unicode)

    def __str__(self) -> str:
        return f'Laptop {self.id} S/N {self.serial_number}'


db.drop_all()
db.create_all()


@app.route('/', methods={'POST'})
def create_computers():
    """Creates two types of PCs, a desktop and a laptop, and returns them."""
    desktop = Desktop(serial_number='d1', internal_lightning=True)
    laptop = Laptop(serial_number='l1', keyboard_layout='USA')

    db.session.add(desktop)
    db.session.add(laptop)
    db.session.flush()
    r = make_response(f'{desktop}\n{laptop}')
    db.session.commit()
    return r


@app.route('/desktops/', methods={'GET'})
def get_desktops():
    return make_response(str(tuple(Desktop.query)))


client = app.test_client()
print('Create 2 subclasses of Computers: 1 Desktop and 1 Laptop')
print('Response:', client.post('/').data)
print('Get all desktops:')
print('Response:', client.get('/desktops/').data)
