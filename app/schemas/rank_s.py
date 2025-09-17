from pydantic import BaseModel
from typing import Optional

# Базовая схема
class RankBase(BaseModel):
    name: str

# Для создания роли
class RankCreate(RankBase):
    pass

# Для обновления роли
class RankUpdate(RankBase):
    pass

# Для ответа
class Rank(RankBase):
    id: int

    class Config:
        from_attributes = True