from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from datetime import date

# --- Схемы для Пользователя (User) ---
class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Схемы для Растений (Plant) ---
class PlantCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    species: str | None = Field(None, max_length=100)
    watering_interval_days: int = Field(ge=1, le=365)
    last_watered_at: date | None = None
    is_favorite: bool = False
    notes: str | None = Field(None, max_length=500)

class PlantUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    species: str | None = Field(None, max_length=100)
    watering_interval_days: int | None = Field(None, ge=1, le=365)
    last_watered_at: date | None = None
    is_favorite: bool | None = None
    notes: str | None = Field(None, max_length=500)

class PlantOut(BaseModel):
    id: int
    name: str
    species: str | None
    watering_interval_days: int
    last_watered_at: date | None
    is_favorite: bool
    notes: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Схемы для Поливов (Watering) ---
class WateringCreate(BaseModel):
    watered_at: date
    amount_ml: int | None = Field(None, ge=0, le=100000)

class WateringOut(BaseModel):
    id: int
    plant_id: int
    watered_at: date
    amount_ml: int | None
    model_config = ConfigDict(from_attributes=True)

# --- Схемы для Статистики ---
class IntervalStat(BaseModel):
    interval_days: int
    count: int

class StatsOut(BaseModel):
    by_interval: list[IntervalStat]
    total_plants: int
    total_waterings: int
    favorite_count: int