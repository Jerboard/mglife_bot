import sqlalchemy as sa
import typing as t

from db.base import METADATA, begin_connection


class UserRow(t.Protocol):
    id: int
    chat_id: int


ChatTable = sa.Table(
    'chats',
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('chat_id', sa.Integer),
)


# возвращает все чаты списком
async def get_all_chats() -> list[int]:
    async with begin_connection () as conn:
        result = await conn.execute(ChatTable.select())
    return [chat_id.chat_id for chat_id in result.all()]


# добавляет чат
async def add_chat(chat_id: int):
    async with begin_connection () as conn:
        result = await conn.execute (ChatTable.select ().where (ChatTable.c.chat_id == chat_id))
        if not result.first():
            await conn.execute (ChatTable.insert ().values (chat_id=chat_id))
