# In Debian & friends, you have to execute this with the postgres user:
# sudo su - postgres
# In Mac, it just works.
dropdb test
createdb test
psql -d test -c "CREATE USER test WITH PASSWORD 'test';"
psql -d test -c "GRANT ALL PRIVILEGES ON DATABASE test TO test"
