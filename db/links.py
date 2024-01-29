import sqlalchemy as sa
import typing as t

from db.base import METADATA, begin_connection

from .flagmans import FlagmanTable


# class LinkRow(t.Protocol):
#     id: int
#     pack_id: int
#     chat_id: int
#     link: str
#     chat_name: str
#     channel_id: int
#     channel_name: str
#     status: str


class LinkRow(t.Protocol):
    id: int
    user_id: int
    chat_id: int
    pack_id: int
    chat_name: str
    link: str


LinkTable = sa.Table(
    'links',
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('user_id', sa.BigInteger),
    sa.Column('chat_id', sa.BigInteger),
    sa.Column('pack_id', sa.Integer),
    sa.Column('chat_name', sa.String(255)),
    sa.Column('link', sa.String(255))
)


# добавляет пользователя
async def add_link(
        user_id: int,
        chat_id: int,
        pack_id: int,
        chat_name: str,
        link: str
) -> None:

    payloads = dict (
        user_id=user_id,
        chat_id=chat_id,
        pack_id=pack_id,
        chat_name=chat_name,
        link=link
    )
    async with begin_connection () as conn:
        await conn.execute (LinkTable.insert ().values (payloads))


# добавляет пользователя
async def update_link(
        row_id: int,
        chat_id: int = None,
        chat_name: str = None,
        link: str = None
) -> None:
    query = LinkTable.update().where(LinkTable.c.id == row_id)

    if chat_id:
        query = query.values(chat_id=chat_id)

    if chat_name:
        query = query.values(chat_name=chat_name)

    if link:
        query = query.values(link=link)
    async with begin_connection () as conn:
        await conn.execute (query)


async def get_user_links(user_id: int) -> tuple[LinkRow]:
    async with begin_connection() as conn:
        result = await conn.execute(LinkTable.select().where(LinkTable.c.user_id == user_id))
    return result.all()


# async def get_user_links(user_id: int) -> tuple[LinkRow]:
#     query = (sa.select(
#         LinkTable.c.id,
#         LinkTable.c.chat_id,
#         LinkTable.c.link,
#         LinkTable.c.pack_id,
#         LinkTable.c.chat_name,
#         FlagmanTable.c.channel_id,
#         FlagmanTable.c.channel_name,
#         FlagmanTable.c.status
#     ).select_from(LinkTable.join(FlagmanTable, LinkTable.c.pack_id == FlagmanTable.c.pack_id)).
#              where(
#         LinkTable.c.user_id == user_id,
#         FlagmanTable.c.status == 'active',
#         LinkTable.c.chat_id == FlagmanTable.c.channel_id
#     ).order_by(LinkTable.c.pack_id))
#
#     async with begin_connection () as conn:
#         result = await conn.execute(query)
#     return result.all()


# далет ссылки пользователя
async def del_users_link(user_id: int, pack_id: int = None) -> None:
    query = LinkTable.delete().where(LinkTable.c.user_id == user_id)
    if pack_id:
        query = query.where(LinkTable.c.pack_id == pack_id)

    async with begin_connection() as conn:
        await conn.execute(query)