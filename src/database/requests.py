from src.database.models import async_session
from src.database.models import User, Action
from sqlalchemy import select, update, delete, desc, text, func


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
async def add_user_drink(session, user_id, action_dt):
    session.add(Action(user_id=user_id, action_type="drink", action_dt=action_dt))
    await session.commit()


@connection
async def get_user_drinks(session, user_id):
    result = await session.scalars(
        select(Action)
        .where(Action.user_id == user_id and Action.action_type == "drink")
        .order_by(desc(Action.action_dt))
        .limit(10)
    )
    return result


@connection
async def get_drink_board(session):
    result = await session.execute(
        select(
            User.tg_name,
            func.max(Action.action_dt).label("last_drink"),
            (func.now() - func.max(Action.action_dt)).label("sober_time")
        )
        .join(Action, User.id == Action.user_id)
        .where(Action.action_type == 'drink')
        .group_by(User.tg_name)
        .order_by("sober_time")
        .limit(15)
    )
    return result
