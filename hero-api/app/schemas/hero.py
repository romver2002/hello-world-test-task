from pydantic import BaseModel, Field, ConfigDict

class HeroIn(BaseModel):
    name: str = Field(min_length=1)

class HeroOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    intelligence: int | None = None
    strength: int | None = None
    speed: int | None = None
    power: int | None = None


