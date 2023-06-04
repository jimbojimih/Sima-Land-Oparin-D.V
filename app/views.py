from datetime import date, datetime
from os import environ
from aiohttp import web
import json
from sqlalchemy import select, insert, update, delete, text, DDL
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.exc import SQLAlchemyError 
from models import users, roles, history
from aiohttp_session import setup, get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography import fernet
import base64
import logging
from aiohttp_swagger import *
from permission import auth_required, admin_required, admin_or_user_record, ALLOWED_METHODS


routes = web.RouteTableDef()
NAME = environ.get('POSTGRES_DB', 'sima_land_task_db')
USER = environ.get('POSTGRES_USER', 'user')
PASSWORD = environ.get('POSTGRES_PASSWORD', 'password')
engine = create_async_engine(f'postgresql+asyncpg://{USER}:{PASSWORD}@db:5432/{NAME}')

#users
@routes.get('/users')
@auth_required
async def get_users(request):
    async with engine.begin() as conn:
        r = await conn.execute(select(users))      
        data = r.fetchall() 

        if not data:
            return web.Response(text="Users not found", status=404)

        data = [{"id":d[0], 'name': d[1], 'last_name': d[2], 'birthdate': d[4].strftime("%d%m%Y"), 
                 'registration_date': d[5].strftime("%d%m%Y"), 'role_id': d[6]} for d in data] 
    return web.json_response(data, status=200)

@routes.get('/users/{user_id}')
@auth_required
@admin_or_user_record
async def get_user(request):
    user_id = int(request.match_info['user_id'])
    async with engine.begin() as conn:
        r = await conn.execute(select(users).where(users.c.user_id==user_id))      
        data = r.fetchone()

        if not data:
            return web.Response(text="User not found", status=404)

        data = {"id":data[0], 'name': data[1], 'last_name': data[2], 'birthdate': data[4].strftime("%d%m%Y"), 
                 'registration_date': data[5].strftime("%d%m%Y"), 'role_id': data[6]}
    return web.json_response(data, status=200)

@routes.post('/users')
async def create_user(request):
    """
    description: New user registration
    tags:
    - Create user
    responses:
        "201":
            description: sucefull
        "400":
            description: Any
    """
    data = await request.json()
    birth = data.get('birthdate')
    if birth:
        data['birthdate'] = datetime.strptime(birth, "%d%m%Y").date()
    
    async with engine.begin() as conn:
        try:
            await conn.execute(insert(users).values(**data))
            return web.Response(status=201, text='sucefull') 

        except SQLAlchemyError:
            return web.Response(status=400, text='Error')        

@routes.patch('/users/{user_id}')
@auth_required
@admin_or_user_record
async def update_user(request):
    user_id = int(request.match_info['user_id'])
    data = await request.json()
    birth = data.get('birthdate')
    if birth:
        data['birthdate'] = datetime.strptime(birth, "%d%m%Y").date()   

    async with engine.begin() as conn:
        try:
            update_query  = update(users).where(users.c.user_id==user_id).values(**data)
            await conn.execute(update_query)

        except SQLAlchemyError:
            return web.Response(status=400, text='Error') 
  
    return web.Response(status=200, text='sucefull')

@routes.delete('/users/{user_id}')
@auth_required
@admin_required
async def update_user(request):
    user_id = int(request.match_info['user_id']) 

    async with engine.begin() as conn:
        update_query = delete(users).where(users.c.user_id==user_id)
        await conn.execute(update_query)    
    
    return web.Response(text="User deleted successfully", status=200)


#roles
@routes.get('/roles')
@auth_required
@admin_required
async def get_roles(request):
    async with engine.begin() as conn:
        r = await conn.execute(select(roles))      
        data = r.fetchall() 

        if not data:
            return web.Response(text="Roles not found", status=404)
        
    return web.json_response(list(map(lambda x: {x[0]:x[1]}, data)))

@routes.get('/roles/{id}')
@auth_required
@admin_required
async def get_role(request):
    id = int(request.match_info['id'])
    async with engine.begin() as conn:
        r = await conn.execute(select(roles).where(roles.c.id==id))      
        data = r.fetchone()

        if not data:
            return web.Response(text="Role not found", status=404)
        
    return web.json_response({data[0]: data[1]})

@routes.post('/roles')
@auth_required
@admin_required
async def create_role(request):
    data = await request.json()

    async with engine.begin() as conn:
        try:
            await conn.execute(insert(roles).values(**data)) 
            return web.Response(status=201, text='sucefull')
        
        except SQLAlchemyError:
            return web.Response(status=400, text='Error')     

@routes.patch('/roles/{id}')
@auth_required
@admin_required
async def update_role(request):
    id = int(request.match_info['id'])
    data = await request.json()  

    async with engine.begin() as conn:
        try:
            update_query = update(roles).where(roles.c.id == id).values(**data)
            await conn.execute(update_query)    
            return web.Response(status=200)

        except SQLAlchemyError:
            return web.Response(status=400, text='Error')  

@routes.delete('/roles/{id}')
@auth_required
@admin_required
async def update_role(request):
    id = int(request.match_info['id']) 

    async with engine.begin() as conn:
        update_query = delete(roles).where(roles.c.id == id)
        await conn.execute(update_query)    
    
    return web.Response(text="Role deleted successfully", status=200)

#auth
@routes.post('/login')
async def login(request):
    """
    description: Login
    tags:
        - Login
    responses:
        "200":
            description: sucefull
        "401":
            description: Invalid username or password
    """    
    print(request)    
    data = await request.json()
    name = data.get('name')
    password = data.get('password')

    async with engine.begin() as conn:
        r = await conn.execute(select(users).where(users.c.name==name))      
        data = r.fetchone()

        if data and data[1] == name and data[3] == password: 
            session = await get_session(request)
            session['id'] = data[0]
            session['user'] = name
            session['role_id'] = data[6]
            session['allowed_methods'] = ALLOWED_METHODS[data[6]]
            return web.Response(text='Logged in', status=200)

    return web.Response(text='Invalid username or password', status=401)

@routes.post('/logout')
@auth_required
async def logout(request):
    session = await get_session(request)
    session.clear()
    response = web.Response(text='Logged out', status=200)
    response.del_cookie('AIOHTTP_SESSION')
    return response


app = web.Application()
logging.basicConfig(level=logging.DEBUG)

key = fernet.Fernet.generate_key()
secret_key = base64.urlsafe_b64decode(key)
app.middlewares.append(session_middleware(EncryptedCookieStorage(secret_key)))

app.add_routes(routes)

setup_swagger(app, swagger_url="/api/v1/docs", ui_version=3)

if __name__ == '__main__':
    web.run_app(app)