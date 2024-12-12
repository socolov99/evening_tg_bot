from src.database.models import async_session
from src.database.models import User, Action
from sqlalchemy import select, update, delete, desc, text
from decimal import Decimal
from src.database.models import SCHEMA_NAME

def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)

    return inner


@connection
async def get_user(session, tg_id):
    return await session.scalar(select(User).where(User.tg_id == tg_id))


@connection
async def set_user(session, tg_id, tg_name):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    if not user:
        session.add(User(tg_id=tg_id, tg_name=tg_name, points=0))
        await session.commit()


@connection
async def add_user_drink(session, user_id):
    session.add(Action(user_id=user_id, action_type="drink"))
    await session.commit()


@connection
async def get_user_drinks(session, user_id):
    return await session.scalars(select(Action).where(Action.user_id == user_id and Action.action_type == "drink")
                                 .order_by(Action.action_dt).limit(10))


@connection
async def get_drink_board(session):
    result = await session.execute(
        text(f"""
          SELECT u.tg_name AS tg_name, MAX(a.action_dt) as last_drink, NOW() - MAX(a.action_dt) as sober_time
          FROM {SCHEMA_NAME}.actions AS a
          JOIN {SCHEMA_NAME}.users AS u
          ON a.user_id = u.id
          WHERE a.action_type = 'drink'
          GROUP BY u.tg_name
          ORDER BY sober_time ASC
          LIMIT 15;
        """)
    )
    return result.fetchall()
