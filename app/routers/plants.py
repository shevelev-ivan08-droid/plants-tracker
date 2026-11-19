from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Plant, User, Watering
from app.schemas import (
    IntervalStat,
    PlantCreate,
    PlantOut,
    PlantUpdate,
    StatsOut,
)

router = APIRouter(prefix="/api/plants", tags=["plants"])


def _get_own_plant(plant_id: int, db: Session, user: User) -> Plant:
    plant = db.scalar(
        select(Plant).where(Plant.id == plant_id, Plant.owner_id == user.id)
    )
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant


@router.get("", response_model=list[PlantOut])
def list_plants(
    search: str | None = Query(None, description="Поиск по названию"),
    is_favorite: bool | None = None,
    sort: str = Query("name", pattern="^(name|last_watered_at|interval|created_at)$"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = select(Plant).where(Plant.owner_id == user.id)

    if search:
        q = q.where(Plant.name.ilike(f"%{search}%"))
    if is_favorite is not None:
        q = q.where(Plant.is_favorite == is_favorite)

    sort_map = {
        "name": Plant.name.asc(),
        "last_watered_at": Plant.last_watered_at.desc(),
        "interval": Plant.watering_interval_days.asc(),
        "created_at": Plant.created_at.desc(),
    }
    q = q.order_by(sort_map[sort]).limit(limit).offset(offset)

    return db.scalars(q).all()


@router.get("/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    by_interval_rows = db.execute(
        select(Plant.watering_interval_days, func.count(Plant.id))
        .where(Plant.owner_id == user.id)
        .group_by(Plant.watering_interval_days)
        .order_by(Plant.watering_interval_days)
    ).all()

    total_plants = db.scalar(
        select(func.count(Plant.id)).where(Plant.owner_id == user.id)
    ) or 0

    favorite_count = db.scalar(
        select(func.count(Plant.id)).where(
            Plant.owner_id == user.id, Plant.is_favorite.is_(True)
        )
    ) or 0

    total_waterings = db.scalar(
        select(func.count(Watering.id))
        .join(Plant, Watering.plant_id == Plant.id)
        .where(Plant.owner_id == user.id)
    ) or 0

    return StatsOut(
        by_interval=[
            IntervalStat(interval_days=row[0], count=row[1])
            for row in by_interval_rows
        ],
        total_plants=total_plants,
        total_waterings=total_waterings,
        favorite_count=favorite_count,
    )


@router.get("/due-today", response_model=list[PlantOut])
def due_today(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Особенность варианта: кого нужно полить сегодня."""
    today = date.today()
    plants = db.scalars(select(Plant).where(Plant.owner_id == user.id)).all()
    due = [
        p for p in plants
        if p.last_watered_at is None
        or (today - p.last_watered_at).days >= p.watering_interval_days
    ]
    return due


@router.get("/{plant_id}", response_model=PlantOut)
def get_plant(
    plant_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return _get_own_plant(plant_id, db, user)


@router.post("", response_model=PlantOut, status_code=status.HTTP_201_CREATED)
def create_plant(
    payload: PlantCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    plant = Plant(**payload.model_dump(), owner_id=user.id) 
    db.add(plant)
    db.commit()
    db.refresh(plant)
    return plant


@router.patch("/{plant_id}", response_model=PlantOut)
def update_plant(
    plant_id: int,
    payload: PlantUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    plant = _get_own_plant(plant_id, db, user)
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(plant, key, value)
    db.commit()
    db.refresh(plant)
    return plant


@router.delete("/{plant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plant(
    plant_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    plant = _get_own_plant(plant_id, db, user)
    db.delete(plant)
    db.commit()