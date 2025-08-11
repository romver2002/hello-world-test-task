from typing import Sequence, Annotated
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import SessionLocal
from app.models.hero import Hero
from app.schemas.hero import HeroIn, HeroOut
from app.clients import superhero as superhero_client

app = FastAPI(title="Heroes API (FastAPI + SQLAlchemy async)")

# Миграции применяются через Alembic; создание схемы на старте не выполняем

async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/hero/", response_model=HeroOut)
async def create_hero(payload: HeroIn, db: AsyncSession = Depends(get_db)):
    name = payload.name.strip()
    try:
        stats = await superhero_client.fetch_powerstats_by_name(name)
    except superhero_client.SuperheroNotFound:
        raise HTTPException(status_code=404, detail=f"Hero '{name}' not found in external API")

    res = await db.execute(select(Hero).where(Hero.name == stats["name"]))
    hero = res.scalar_one_or_none()

    if hero is None:
        hero = Hero(
            name=stats["name"],
            intelligence=stats["intelligence"],
            strength=stats["strength"],
            speed=stats["speed"],
            power=stats["power"],
        )
        db.add(hero)
        await db.commit()
        await db.refresh(hero)
        return JSONResponse(HeroOut.model_validate(hero).model_dump(), status_code=status.HTTP_201_CREATED)

    return HeroOut.model_validate(hero)

def _numeric_filters(col, value: str | None, gte: int | None, lte: int | None):
    conds = []
    if value:
        v = value.strip()
        try:
            if v.startswith(">="):
                conds.append(col >= int(v[2:]))
            elif v.startswith("<="):
                conds.append(col <= int(v[2:]))
            else:
                conds.append(col == int(v))
        except ValueError:
            pass
    if gte is not None:
        conds.append(col >= gte)
    if lte is not None:
        conds.append(col <= lte)
    return and_(*conds) if conds else None

@app.get("/hero/", response_model=list[HeroOut])
async def list_heroes(
    name: str | None = Query(default=None, description="Точное совпадение имени"),
    # поддержка опечатки из ТЗ
    intelligence: str | None = None,
    intellegence: Annotated[str | None, Query(alias="intellegence")] = None,
    strength: str | None = None,
    speed: str | None = None,
    power: str | None = None,
    # дополнительные формы (не обязаны по ТЗ, но поддержаны)
    intelligence_min: int | None = None,
    intelligence_max: int | None = None,
    strength_min: int | None = None,
    strength_max: int | None = None,
    speed_min: int | None = None,
    speed_max: int | None = None,
    power_min: int | None = None,
    power_max: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    # консолидируем alias
    intelligence = intelligence or intellegence

    q = select(Hero)
    conds = []
    if name:
        conds.append(Hero.name == name)

    for col, val, gte, lte in [
        (Hero.intelligence, intelligence, intelligence_min, intelligence_max),
        (Hero.strength, strength, strength_min, strength_max),
        (Hero.speed, speed, speed_min, speed_max),
        (Hero.power, power, power_min, power_max),
    ]:
        c = _numeric_filters(col, val, gte, lte)
        if c is not None:
            conds.append(c)

    if conds:
        q = q.where(and_(*conds))

    res = await db.execute(q)
    rows: Sequence[Hero] = res.scalars().all()
    if not rows:
        raise HTTPException(status_code=404, detail="No heroes matched filters")

    return [HeroOut.model_validate(h) for h in rows]


