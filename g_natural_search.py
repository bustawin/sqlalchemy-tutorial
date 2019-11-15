from typing import Tuple

from flask import Flask, make_response, request
from flask_sqlalchemy import SQLAlchemy
from sqla_psql_search import search as s
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import TSVECTOR

app = Flask(__name__)  # Create Flask App
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test:test@localhost/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False


# postgresql://user@pass:host/db
class MySQLAlchemy(SQLAlchemy):
    UUID = postgresql.UUID  # Add psql's UUID type
    CASCADE_DEL = 'save-update, merge, delete-orphan'


db = MySQLAlchemy(app, session_options={'autoflush': False})


class Computer(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Computer info
    type = db.Column(db.Unicode)
    serial_number = db.Column(db.Unicode)
    model = db.Column(db.Unicode)
    manufacturer = db.Column(db.Unicode)

    # Component info
    """Hard drive size in MB."""
    cpu_model = db.Column(db.Unicode)
    gpu_model = db.Column(db.Unicode)

    def __str__(self) -> str:
        return f'PC {self.id} {self.type}'

    def __repr__(self) -> str:
        return str(self)


class SearchTokens(db.Model):
    id = db.Column(db.Integer, db.ForeignKey(Computer.id, ondelete='CASCADE'), primary_key=True)
    description = db.Column(TSVECTOR, nullable=False)
    components = db.Column(TSVECTOR, nullable=False)

    trip = db.relationship(Computer, primaryjoin=Computer.id == id)

    __table_args__ = (
        db.Index('description-gist', description, postgresql_using='gist'),
        db.Index('components-gist', components, postgresql_using='gist'),
        {
            'prefixes': ['UNLOGGED']
            # Accelerate temporal tables
            # Can cause table to empty on run
        }
    )


def generate_search_tokens(pc: Computer):
    """Compute and save the tokens from the passed-in computer."""
    desc_tokens = [
        (str(pc.id), s.Weight.A),  # It can be a literal
        (Computer.type, s.Weight.B),
        (Computer.serial_number, s.Weight.A),
        (Computer.model, s.Weight.A),
        (Computer.manufacturer, s.Weight.A),
    ]
    desc_field_query = db.session.query(s.vectorize(*desc_tokens)).filter(Computer.id == pc.id)

    comp_tokens = [
        (Computer.cpu_model, s.Weight.C),
        (Computer.gpu_model, s.Weight.C)
    ]
    comp_field_query = db.session.query(s.vectorize(*comp_tokens)).filter(Computer.id == pc.id)

    search_token = {
        'description': desc_field_query.one_or_none(),
        'components': comp_field_query.one_or_none()
    }

    # A raw sqlalchemy query using postgresql unique capabilities
    # (on_conflict_do_update)
    insert = postgresql.insert(SearchTokens.__table__) \
        .values(id=pc.id, **search_token) \
        .on_conflict_do_update(constraint='search_tokens_pkey', set_=search_token)
    db.session.execute(insert)


def search(text: str) -> Tuple[Computer, ...]:
    """Search the passed-in text to the devices."""
    # Note that the filter is only on SearchTokens
    # Recent PSQL versions can sanitize and prepare unsafe text
    query = Computer.query.join(SearchTokens).filter(
        s.match(SearchTokens.description, text) | s.match(SearchTokens.components, text)
    ).order_by(
        s.rank(SearchTokens.description, text) + s.rank(SearchTokens.components, text)
    )
    return tuple(query)


db.drop_all()
db.create_all()


@app.route('/', methods={'POST'})
def create_computers():
    """Creates two types of PCs, a desktop and a laptop, and returns them."""
    pc1 = Computer(type='Laptop',
                   serial_number='foo', model='bar', manufacturer='baz', cpu_model='intel',
                   gpu_model='nvidia')
    pc2 = Computer(type='Desktop',
                   serial_number='spam', model='python', manufacturer='course', cpu_model='amd',
                   gpu_model='ati')

    db.session.add(pc1)
    db.session.add(pc2)
    db.session.flush()
    generate_search_tokens(pc1)
    generate_search_tokens(pc2)
    db.session.commit()
    return make_response('ok')


@app.route('/', methods={'GET'})
def search_computers():
    search_text = request.args['search']
    computers = search(search_text)
    return make_response(str(computers))


# Test
client = app.test_client()
print('Create computers:')
print('Response:', client.post('/').data)
print('Search computers:')
print('Response:', client.get('/?search=spam').data)
