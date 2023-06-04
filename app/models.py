from sqlalchemy import(
	MetaData,
	create_engine, 
	Integer, 
	String, 
	Date, 
	DateTime,
	Column, 
	ForeignKey,
	Table,
	insert,
	select,
	JSON,
	text,
)
from datetime import date, datetime
from os import environ

NAME = environ.get('POSTGRES_DB', 'sima_land_task_db')
USER = environ.get('POSTGRES_USER', 'user')
PASSWORD = environ.get('POSTGRES_PASSWORD', 'password')
engine = create_engine(f'postgresql+psycopg2://{USER}:{PASSWORD}@db:5432/{NAME}')

metadata_obj = MetaData()

users = Table("user", metadata_obj,
    Column("user_id", Integer, primary_key=True), 
    Column("name", String(16), nullable=False, unique=True),
    Column("last_name", String(16)),
    Column("password", String(50), nullable=False),    
    Column("birthdate", Date, nullable=False),
    Column("registration_date", Date, default=date.today),
    Column("role_id", Integer, ForeignKey('role.id'), nullable=False),
)

roles = Table("role", metadata_obj,
    Column("id", Integer, primary_key=True), 
    Column("name", String(16), unique=True, nullable=False),
)

history = Table('history', metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('old', JSON),
    Column('new', JSON),
)

metadata_obj.create_all(engine)

if __name__ == '__main__':

	trigger = text('''
	CREATE OR REPLACE FUNCTION log_user_changes() 
	RETURNS TRIGGER AS $$
	BEGIN
	  IF NEW <> OLD THEN
	    INSERT INTO history(old, new)
	    VALUES (
	      to_json(OLD),
	      to_json(NEW)
	    );
	  END IF;
	  RETURN NEW;
	END;
	$$ LANGUAGE plpgsql;

	CREATE TRIGGER user_changes 
	AFTER UPDATE ON "user"
	FOR EACH ROW
	EXECUTE PROCEDURE log_user_changes();
	''')

	with engine.begin() as conn:
	    conn.execute(trigger)