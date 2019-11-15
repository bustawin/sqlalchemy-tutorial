"""
This example is from `TutorialsPoint <https://www.tutorialspoint.com/
sqlalchemy/sqlalchemy_core_expression_language.htm>`_
"""

from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine

engine = create_engine('sqlite://', echo=True)
meta = MetaData()  # Create a sandbox (where SQLA stores Table... the DB Schema)

students = Table(
    'students', meta,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('lastname', String),
)
conn = engine.connect()

meta.create_all(engine)  # Create the tables

ins = students.insert().values(name='Ravi', lastname='Kapoor')
print(conn.execute(ins))

conn1 = engine.connect()
s = students.select()
result = conn1.execute(s)

print('Students:')
for row in result:
    print(row)
