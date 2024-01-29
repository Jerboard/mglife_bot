import sqlalchemy as sa
import typing as t

from datetime import date

from db.base import METADATA, begin_connection


class FlagmanRow(t.Protocol):
    id: int
    pack_id: int
    start_date: str
    status: str
    pack_name: str
    channel_name: str
    channel_button: str
    channel_id: int


FlagmanTable = sa.Table(
    'flagman_chats',
    METADATA,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('pack_id', sa.Integer),
    sa.Column('start_date', sa.String(255)),
    sa.Column('status', sa.String(255)),
    sa.Column('pack_name', sa.String(255)),
    sa.Column('channel_name', sa.String(255)),
    sa.Column('channel_button', sa.String(255)),
    sa.Column('channel_id', sa.BigInteger),
)


# Добавить флагман
async def add_flagman(
        start_date: str,
        status: str,
        pack_id: int,
        pack_name: str,
        channel_name: str,
        channel_id: int,
        channel_button
        ) -> int:
    async with begin_connection() as conn:
        result = await conn.execute(
            FlagmanTable.insert().values(
                start_date=start_date,
                status=status, 
                pack_id=pack_id,
                pack_name=pack_name,
                channel_name=channel_name,
                channel_id=channel_id,
                channel_button=channel_button
            )
        )

    return result.inserted_primary_key_rows[0][0]
        
        
# Обновить флагман
async def update_flagman_pack(
        pack_id: int,
        start_date: str = None,
        status: str = None,
        pack_name: str = None, 
        ) -> None:
    query = FlagmanTable.update().where(
        FlagmanTable.c.pack_id == pack_id,
        FlagmanTable.c.status == 'active')
    
    if start_date:
        query = query.values(start_date=start_date)
        
    if status:
        query = query.values(status=status)
        
    if pack_name:
        query = query.values(pack_name=pack_name)
    
    async with begin_connection() as conn:
        await conn.execute(query)


# Добавить канал
async def update_flagman(
        row_id: int,
        status: str = None,
        button_name: str = None,
) -> None:
    query = FlagmanTable.update ().where (
        FlagmanTable.c.id == row_id,
        FlagmanTable.c.status == 'active')

    if status:
        query = query.values (status=status)

    if button_name:
        query = query.values (button_name=button_name)

    async with begin_connection () as conn:
        await conn.execute (query)


# все активные флагманы
async def get_all_flagman(pack_id: int = 0) -> tuple[FlagmanRow]:
    query = FlagmanTable.select().where(FlagmanTable.c.status == 'active')

    if pack_id:
        query = query.where(FlagmanTable.c.pack_id == pack_id)

    async with begin_connection() as conn:
        result = await conn.execute(query)
    return result.all()


# флагман по ид
async def get_flagman(row_id: int) -> t.Union[FlagmanRow, None]:
    async with begin_connection () as conn:
        result = await conn.execute (FlagmanTable.select ().where (FlagmanTable.c.id == row_id))
    return result.first ()


# флагман по чатид
async def get_flagman_channel(channel_id: int) -> t.Union[FlagmanRow, None]:
    async with begin_connection () as conn:
        result = await conn.execute (
            FlagmanTable.select ().where (
                FlagmanTable.c.channel_id == channel_id,
                FlagmanTable.c.status == 'active'))
    return result.first ()


# флагман по ид
async def get_pack_info(pack_id: int) -> t.Union[FlagmanRow, None]:
    async with begin_connection () as conn:
        result = await conn.execute (FlagmanTable.select ().where (
            FlagmanTable.c.pack_id == pack_id,
            FlagmanTable.c.status == 'active'
        ))
    return result.first ()


# отключает флагманы
async def inactive_flagman(pack_id: int = 0, row_id: int = 0) -> None:
    query = FlagmanTable.update().values(status='inactive')

    if pack_id:
        query = query.where(FlagmanTable.c.pack_id == pack_id)

    if row_id:
        query = query.where (FlagmanTable.c.id == row_id)

    async with begin_connection() as conn:
        await conn.execute(query)


# флагман по ид
async def del_pack_row(row_id: int) -> None:
    async with begin_connection () as conn:
        await conn.execute (FlagmanTable.delete ().where (FlagmanTable.c.id == row_id))
