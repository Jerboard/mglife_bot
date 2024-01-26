import sqlalchemy as sa
import typing as t

from db.base import METADATA, begin_connection


class LinkRow(t.Protocol):
    id: int
    user_id: int
    chat_id: int
    chat_name: str
    link: str


LinkTable = sa.Table(
    'links',
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('user_id', sa.BigInteger),
    sa.Column('chat_id', sa.BigInteger),
    sa.Column('chat_name', sa.String(255)),
    sa.Column('link', sa.String(255))
)


# добавляет пользователя
async def add_link(
        user_id: int,
        chat_id: int,
        chat_name: str,
        link: str
) -> None:

    payloads = dict (
        user_id=user_id,
        chat_id=chat_id,
        chat_name=chat_name,
        link=link
    )
    async with begin_connection () as conn:
        await conn.execute (LinkTable.insert ().values (payloads))


async def get_user_links(user_id: int) -> tuple[LinkRow]:
    async with begin_connection () as conn:
        result = await conn.execute (
            LinkTable.select().where(LinkTable.c.user_id == user_id)
        )
    return result.all()
