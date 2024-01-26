import sqlalchemy as sa
import typing as t

from db.base import METADATA, begin_connection


class UserRow(t.Protocol):
    id: int
    tg_id: int
    full_name: str
    username: str
    status: str
    gc_id: int
    email: str
    list: str


UsersTable = sa.Table(
    'users',
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('tg_id', sa.BigInteger),
    sa.Column('full_name', sa.String(128)),
    sa.Column('username', sa.String(32)),
    sa.Column('status', sa.String(50), default='free'),
    sa.Column('gc_id', sa.BigInteger),
    sa.Column('email', sa.String(255)),
    sa.Column('list', sa.String(50)),

)


# добавляет пользователя
async def add_user(
        tg_id: int,
        full_name: str,
        username: str,
        status: str,
        list_gc: str,
        gc_id: int = None,
        email: str = None
) -> None:

    payloads = dict (
        tg_id=tg_id,
        full_name=full_name,
        username=username,
        status=status,
        gc_id=gc_id,
        email=email,
        list=list_gc
    )
    async with begin_connection () as conn:
        await conn.execute (UsersTable.insert ().values (payloads))


# добавляет пользователя
async def del_user(user_id: int) -> None:
    async with begin_connection () as conn:
        await conn.execute (UsersTable.delete ().where (UsersTable.c.id == user_id))


# проверяет почту
async def get_email_info(email: str) -> UserRow:
    async with begin_connection () as conn:
        result = await conn.execute(UsersTable.select().where(UsersTable.c.email.ilike(email)))
    return result.first()


# инфо о пользователе
async def get_user_info(user_id: int) -> UserRow:
    async with begin_connection () as conn:
        result = await conn.execute(UsersTable.select().where(UsersTable.c.tg_id == user_id))
    return result.first()


# обновляет статус
async def ban_email(email: str) -> None:
    async with begin_connection () as conn:
        await conn.execute (UsersTable.update ().where (UsersTable.c.email == email).values(status='ban'))


# добавляет почту
async def add_email(gc_id: int, email: str) -> None:
    async with begin_connection () as conn:
        await conn.execute (UsersTable.insert ().values (email=email, gc_id=gc_id))
