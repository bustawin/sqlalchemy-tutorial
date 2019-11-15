import enum
from datetime import datetime

from flask import Flask, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

app = Flask(__name__)  # Create Flask App
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test:test@localhost/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app, session_options={'autoflush': False})


class Language(enum.Enum):
    # ESP, EN... are stored in PSQL as an "Enumerated Type"
    ESP = 'Spanish'
    EN = 'English'


class Trip(db.Model):
    name = db.Column(db.Unicode, primary_key=True)
    start_time = db.Column(db.TIMESTAMP(timezone=True))
    end_time = db.Column(db.TIMESTAMP(timezone=True))

    @validates('end_time')
    def validate_end_time(self, _, end_time: datetime):
        if self.start_time and end_time <= self.start_time:
            raise ValueError('The trip cannot finish before it starts.')
        return end_time

    @validates('start_time')
    def validate_start_time(self, _, start_time: datetime):
        if self.end_time and start_time >= self.end_time:
            raise ValueError('The trip cannot start after it finished.')
        return start_time

    def __str__(self) -> str:
        return f'User {self.name} from {self.start_time} to {self.end_time}'


db.drop_all()
db.create_all()


@app.route('/', methods={'POST'})
def create_trip():
    """Creates a trip and returns it."""
    trip = Trip(name='foo',
                start_time=datetime(year=2019, month=10, day=10),
                end_time=datetime(year=2019, month=10, day=11))
    db.session.add(trip)
    db.session.flush()
    r = make_response(str(trip))
    db.session.commit()
    return r


client = app.test_client()
print('Response:', client.post('/').data)
