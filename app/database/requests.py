from collections.abc import Callable
from decimal import Decimal

from sqlalchemy import select, update

from app.database import AiModel, User, async_session
from app.handlers.get_loggers import get_logger

logger = get_logger(__name__)


def connection(func: Callable) -> Callable:
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)

    return inner


@connection
async def set_user(session, tg_id):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))

    if not user:
        session.add(User(tg_id=tg_id, balance="100"))
        await session.commit()


@connection
async def get_user(session, tg_id):
    return await session.scalar(select(User).where(User.tg_id == tg_id))


@connection
async def get_users(session):
    return await session.scalars(select(User))


@connection
async def calculate(session, tokens_sum, model_name, user):
    model = await session.scalar(select(AiModel).where(AiModel.name == model_name))
    spends = Decimal(Decimal(model.price) * Decimal(tokens_sum))
    logger.info(f"Было затрачено: {spends}")

    new_balance = Decimal(Decimal(user.balance) - spends)

    await session.execute(
        update(User).where(User.id == user.id).values(balance=str(new_balance))
    )
    await session.commit()
