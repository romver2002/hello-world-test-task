import asyncio
from sqlalchemy import select
from app.celery_app import celery_app
from app.clients import superhero as sh
from app.clients.openrouter import generate_hero_post
from app.clients.telegram import send_message
from app.core.db import SessionLocal
from app.models.hero import Hero

@celery_app.task(name="app.tasks.post_hero.post_one_hero")
def post_one_hero(name: str | None = None) -> None:
    async def run() -> None:
        async with SessionLocal() as db:
            # если имя не передано — берём любого героя из БД; если пусто — используем Batman
            actual_name = name
            if not actual_name:
                res = await db.execute(select(Hero).limit(1))
                hero = res.scalars().first()
                actual_name = hero.name if hero else "Batman"

            stats = await sh.fetch_powerstats_by_name(actual_name)

            # ensure в БД существование записи
            res2 = await db.execute(select(Hero).where(Hero.name == stats["name"]))
            exists = res2.scalars().first()
            if not exists:
                db.add(Hero(
                    name=stats["name"],
                    intelligence=stats["intelligence"],
                    strength=stats["strength"],
                    speed=stats["speed"],
                    power=stats["power"],
                ))
                await db.commit()

            text = await generate_hero_post(stats["name"], stats)
            await send_message(text)

    asyncio.run(run())


@celery_app.task(name="app.tasks.post_hero.post_all_heroes")
def post_all_heroes() -> None:
    async def run() -> None:
        async with SessionLocal() as db:
            res = await db.execute(select(Hero.name))
            names = [row for row in res.scalars().all()] or ["Batman"]
        # последовательно публикуем пост по каждому герою
        for n in names:
            awaitable = asyncio.to_thread(lambda: post_one_hero.apply_async(kwargs={"name": n}))
            await awaitable
    asyncio.run(run())


