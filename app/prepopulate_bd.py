from datetime import date, datetime
from os import environ
from models import users, roles, history
from sqlalchemy import(
	create_engine, 
	insert,
)
from sqlalchemy.ext.asyncio import create_async_engine


NAME = environ.get('POSTGRES_DB', 'sima_land_task_db')
USER = environ.get('POSTGRES_USER', 'user')
PASSWORD = environ.get('POSTGRES_PASSWORD', 'password')
engine = create_engine(f'postgresql+psycopg2://{USER}:{PASSWORD}@db:5432/{NAME}')

with engine.connect() as conn:
	
	conn.execute(insert(roles), [
		{'name': 'Admin'},
		{'name': 'User'},
	])
	
	conn.execute(insert(users), [
		{'name': 'admin', 
		'password': 'admin',
		'last_name': '', 
		'birthdate': date(2023,5,30),
		'role_id': 1
		},
		{'name': 'user', 
		'last_name': 'user_last_name', 
		'password': 'user',
		'birthdate': date(2020,5,30),
		'role_id': 2
		},
		{'name': 'user2', 
		'last_name': 'user_last_name2', 
		'password': 'user2',
		'birthdate': date(2022,5,30),
		'role_id': 2
		},
	])

	conn.commit()