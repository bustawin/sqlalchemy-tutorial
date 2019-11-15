from flask import Flask, make_response, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)  # Create Flask App
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'  # In memory SQLITE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # SQLA will complain if this is True
app.config['SQLALCHEMY_ECHO'] = False  # Print all DB transactions

db = SQLAlchemy(app, session_options={
    'autoflush': False
})  # Create a SQLAlchemy sandbox (i.e. sqlalchemy's meta + flask stuff)


class Computer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.Unicode, nullable=False)
    manufacturer = db.Column(db.Unicode, nullable=False)
    serial_number = db.Column(db.Unicode, nullable=False)

    def __repr__(self) -> str:
        return f'<Computer {self.id} model={self.model} S/N={self.serial_number}>'


db.create_all()


@app.route('/', methods={'POST'})
def post_device():
    """Creates a PC, adding it to the database and returning it.

    You can pass-in the SN as the URL query.
    """
    pc = Computer(model='foo', manufacturer='bar')
    pc.serial_number = 'sn1'
    # Other fields are initialized as None
    db.session.add(pc)
    db.session.flush()
    r = make_response(str(pc))
    db.session.commit()
    return r


@app.route('/<int:id>')
def get_device(id: int):
    """Gets a PC by its ID."""
    select_query = Computer.query.filter(Computer.id == id)
    pc = select_query.one()
    return make_response(str(pc))


@app.route('/')
def get_devices():
    """Gets all computers."""
    return make_response(str(tuple(Computer.query)))


# Tests
client = app.test_client()
print('Create one device (ID = 1):')
print('Response:', client.post('/').data)

print('Get the first device (ID = 1):')
print('Response:', client.get('/1').data)

print('Get all devices (although there is only one):')
print('Response:', client.get('/').data)


# Complicated filter
@app.route('/wtf/<int:id>')
def get_device_wtf_query(id: int):
    """Gets a PC by its ID."""
    pc = Computer.query.filter((Computer.model != 'xyz') & (Computer.model != None)).one()
    return make_response(str(pc))


print('Complicated filter:')
print('Response:', client.get('/wtf/1').data)
