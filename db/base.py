import typing as t
import sqlalchemy as sa

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from init import ENGINE

METADATA = sa.MetaData()


def begin_connection() -> t.AsyncContextManager[AsyncConnection]:
    return ENGINE.begin()


async def init_models():
    async with ENGINE.begin() as conn:
        await conn.run_sync(METADATA.create_all)

