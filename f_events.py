from typing import Optional

from flask import Flask, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.orm.events import AttributeEvents

app = Flask(__name__)  # Create Flask App
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test:test@localhost/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app, session_options={'autoflush': False})


class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    responsible_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # Note that I write user in small caps because it refers to the table

    travelers = db.relationship(lambda: User,
                                backref=db.backref('trips', lazy=True, collection_class=set),
                                secondary=lambda: Traveler.__table__,
                                collection_class=set)
    responsible = db.relationship(lambda: User,
                                  primaryjoin='Trip.responsible_id == User.id')
    """A responsible is a traveler."""

    def __str__(self) -> str:
        return f'Trip {self.id} travelers: {self.travelers}, responsible: {self.responsible}'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)


class Traveler(db.Model):
    trip_id = db.Column(db.Integer, db.ForeignKey(Trip.id), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True)
    # Yes, responsible could be a boolean here
    # but stay with me for the sake of the example... ;-)


@event.listens_for(Trip.responsible, AttributeEvents.set.__name__, propagate=True)
def update_responsible_as_traveler(target: Trip, value: Optional[User], *_):
    """Sets a responsible user as a traveler."""
    # Constraint: The responsible is a traveller
    if value:
        target.travelers.add(value)


db.drop_all()
db.create_all()


@app.route('/', methods={'POST'})
def create_user_trip_responsible():
    """Create an user, create a trip, and set the user as the responsible. Returns trip."""
    user = User(name='foo')
    trip = Trip()
    trip.responsible = user
    db.session.add(user)
    db.session.flush()
    r = make_response(str(trip))
    db.session.commit()
    return r


client = app.test_client()
print('Create user, create trip, set responsible of trip to user:')
print('Response:', client.post('/').data)


# Exercise
@event.listens_for(Trip.travelers, AttributeEvents.remove.__name__, propagate=True)
def remove_responsible_if_no_traveler(target: Trip, value: User, *_):
    """Removes the responsible of the group if it ends up not
    being a traveler."""
    # todo


@app.route('/trip/<int:id>/travelers/', methods={'DELETE'})
def remove_all_travelers(id: int):
    trip = Trip.query.filter(Trip.id == id).one()
    trip.travelers.clear()
    db.session.flush()
    r = make_response(str(trip))
    db.session.commit()
    return r


print('Remove responsible:')
print('Response:', client.delete('/trip/1/travelers/').data)
