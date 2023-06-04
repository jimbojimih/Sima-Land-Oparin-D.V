from aiohttp_session import get_session
from os import environ
from aiohttp import web
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select
from models import users, roles


NAME = environ.get('POSTGRES_DB', 'sima_land_task_db')
USER = environ.get('POSTGRES_USER', 'user')
PASSWORD = environ.get('POSTGRES_PASSWORD', 'password')
engine = create_async_engine(f'postgresql+asyncpg://{USER}:{PASSWORD}@db:5432/{NAME}')

ALLOWED_METHODS = {
    1 : ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'], #Admin example
    2 : ['GET', 'POST', ], #User example
}

def auth_required(handler):
    async def check_login(request, *args, **kwargs):
        session = await get_session(request)
        user_id = session.get('id')

        if user_id:
            return await handler(request)

        return web.Response(text='Forbidden', status=403)       

    return check_login
    
def admin_required(handler):
    async def check_admin(request, *args, **kwargs):
        session = await get_session(request)
        role_id = session.get('role_id')

        async with engine.begin() as conn:
            r = await conn.execute(select(roles).where(roles.c.id==role_id))      
            data = r.fetchone()
            role = data[1]

        if role == 'Admin':
            return await handler(request)

        return web.Response(text='Forbidden', status=403)       

    return check_admin

def admin_or_user_record(handler):
    async def check_admin_or_user_record(request, *args, **kwargs):
        rout_id = int(request.match_info['user_id'])

        session = await get_session(request)
        user_id = session.get('id')
        role_id = session.get('role_id')

        async with engine.begin() as conn:
            r = await conn.execute(select(roles).where(roles.c.id==role_id))      
            data = r.fetchone()
            role = data[1]

        if role == 'Admin' or user_id == rout_id:
            return await handler(request)

        return web.Response(text='Forbidden', status=403)       

    return check_admin_or_user_record