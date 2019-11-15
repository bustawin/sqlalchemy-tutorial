from flask import Flask, make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)  # Create Flask App
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test:test@localhost/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app, session_options={'autoflush': False})


class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    travelers = db.relationship(lambda: User,
                                backref=db.backref('trips', lazy=False, collection_class=set),
                                secondary=lambda: Traveler.__table__,
                                collection_class=set)

    def __str__(self) -> str:
        return f'Trip {self.id} travelers: {self.travelers}'

    def __repr__(self) -> str:
        return str(self)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)

    # trips = relationship to Trip through Trip's backref

    def __str__(self) -> str:
        return f'User {self.id} {self.name}, trips: {self.trips}'


class Traveler(db.Model):
    trip_id = db.Column(db.Integer, db.ForeignKey(Trip.id), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True)


db.drop_all()
db.create_all()


@app.route('/', methods={'POST'})
def create():
    u1 = User(name='Foo')
    u2 = User(name='Bar')
    trip = Trip()
    trip.travelers.add(u1)
    trip.travelers.add(u2)
    db.session.add(trip)  # We don't have to explicitly add users to session
    db.session.flush()
    r = make_response(str(trip))
    db.session.commit()
    return r


@app.route('/trip/', methods={'GET'})
def get_trip():
    return make_response(str(Trip.query.first()))


@app.route('/users/', methods={'GET'})
def get_users():
    return make_response(str(User.query.first()))


# Tests
client = app.test_client()
print('Create one user:')
print('Response:', client.post('/').data)
print('Get trip:')
print('Response:', client.get('/trip/').data)
print('Get users:')
print('Response:', client.get('/users/').data)
