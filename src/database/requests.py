from src.database.models import async_session
from src.database.models import User, Action
from sqlalchemy import select, desc, func, extract
from datetime import datetime

def connection(function):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await function(session, *args, **kwargs)

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
    result = await session.execute(
        select(
            func.distinct(Action.action_dt).label("action_dt")
        )
        .where(Action.user_id == user_id and Action.action_type == "drink")
        .order_by(desc("action_dt"))
        .limit(15)
    )
    return result


@connection
async def get_drink_board(session):
    result = await session.execute(
        select(
            User.id,
            func.max(func.coalesce(User.user_full_name, User.tg_name, "Безымянный")).label("user_name"),
            func.max(Action.action_dt).label("last_drink"),
            func.max(Action.action_reg_dt).label("action_reg_dt"),
            (func.now() - func.max(Action.action_dt)).label("sober_time")
        )
        .join(Action, User.id == Action.user_id)
        .where(Action.action_type == 'drink')
        .group_by(User.id)
        .order_by("sober_time", desc("action_reg_dt"))
        .limit(30)
    )
    return result


@connection
async def get_month_drink_stats(session, month: int = None):
    # Если месяц не передан, берем текущий месяц
    if month is None:
        month_filter = datetime.now().month
        year_filter = datetime.now().year
    else:
        month_filter = month
        year_filter = datetime.now().year

    month_actions = (
        select(
            Action.user_id, Action.action_dt
        )
        .filter(
            Action.action_type == 'drink',
            extract('month', Action.action_dt) == month_filter,
            extract('year', Action.action_dt) == year_filter
        )
        .subquery()
    )

    result = await session.execute(
        select(
            User.id,
            func.max(func.coalesce(User.user_full_name, User.tg_name, "Безымянный")).label("user_name"),
            func.count(func.distinct(month_actions.c.action_dt)).label("drink_days_qty")
        )
        .join(month_actions, User.id == month_actions.c.user_id, isouter=True)
        .group_by(User.id)
        .order_by(desc("drink_days_qty"))
        .limit(30)
    )
    return result
