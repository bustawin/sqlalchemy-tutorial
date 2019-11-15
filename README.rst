SQLAlchemy tutorial
###################
Tutorial for SQLAlchemy as part of the PyDayBCN.

Installation
************

You need `PostgreSQL 11 or newer <https://www.postgresql.org/download/>`_
and Python 3.7 or newer (3.6 should work but I have not tested it).

.. code-block::
   sh

  git clone https://github.com/bustawin/sqlalchemy-tutorial
  cd sqlalchemy-tutorial
  pip3 install -e . -r requirements.txt

Optionally, you can have it inside a virtualenv.

We will use a test dummy database in Postgres. Creating this database
differs from OS:

- Mac: Execute the ``init-db.sh`` file that exists in this repo: ``sh init-db.sh``.
- Linux: As in Mac. However, in some distros like Debian, you will need
  to switch to the Postgres user, like ``sudo su postgres``, to be able to
  write these commands, as your regular user doesn't have access to the whole
  PSQL database.
- Windows: Just copy and paste the commands of the ``init-db.sh`` file
  in your CMD.

I will be available in class to help you with any problem regarding
the installation, so don't worry :-).
As a minimum, have Postgres, Python, and Git downloaded.

.. important::

  Remember to ``git pull`` before the class to ensure you have the latest
  version and re-execute ``pip3 install -e . -r requirements.txt``
