"""
Objective: understand how to create a MaterializedView / View in SQLA.

Adapted from the `tests <https://github.com/kvesteri/sqlalchemy-utils/
blob/master/tests/test_views.py>`_ in sqlalchemy-utils.
"""

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import (
    create_materialized_view,
    create_view,
    refresh_materialized_view
)

engine = create_engine('postgresql://test:test@localhost/test', echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)


class Article(Base):
    __tablename__ = 'article'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    author_id = sa.Column(sa.Integer, sa.ForeignKey(User.id))
    author = sa.orm.relationship(User)


class ArticleMV(Base):
    __table__ = create_materialized_view(
        name='article_mv',
        selectable=sa.select(
            [
                Article.id,
                Article.name,
                User.id.label('author_id'),
                User.name.label('author_name')
            ],
            from_obj=(
                Article.__table__
                    .join(User, Article.author_id == User.id)
            )
        ),
        metadata=Base.metadata,
        indexes=[sa.Index('article_mv_id_idx', 'id')]
    )


class ArticleView(Base):
    __table__ = create_view(
        name='article_view',
        selectable=sa.select(
            [
                Article.id,
                Article.name,
                User.id.label('author_id'),
                User.name.label('author_name')
            ],
            from_obj=(
                Article.__table__
                    .join(User, Article.author_id == User.id)
            )
        ),
        metadata=Base.metadata
    )


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

# Test
session = Session()

article = Article(
    name='Some article',
    author=User(name='Some user')
)
session.add(article)
session.commit()
refresh_materialized_view(session, 'article_mv')
materialized = session.query(ArticleMV).first()
assert materialized.name == 'Some article'
assert materialized.author_name == 'Some user'

article = Article(
    name='Some article',
    author=User(name='Some user')
)
session.add(article)
session.commit()
row = session.query(ArticleView).first()
assert row.name == 'Some article'
assert row.author_name == 'Some user'
