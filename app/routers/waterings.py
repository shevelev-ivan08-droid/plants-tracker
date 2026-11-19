from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Plant, User, Watering
from app.schemas import WateringCreate, WateringOut

router = APIRouter(prefix="/api", tags=["waterings"])


def _get_own_plant(plant_id: int, db: Session, user: User) -> Plant:
    plant = db.scalar(
        select(Plant).where(Plant.id == plant_id, Plant.owner_id == user.id)
    )
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant


@router.get("/plants/{plant_id}/waterings", response_model=list[WateringOut])
def list_waterings(
    plant_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _get_own_plant(plant_id, db, user)
    rows = db.scalars(
        select(Watering)
        .where(Watering.plant_id == plant_id)
        .order_by(Watering.watered_at.desc())
    ).all()
    return rows


@router.post(
    "/plants/{plant_id}/waterings",
    response_model=WateringOut,
    status_code=status.HTTP_201_CREATED,
)
def create_watering(
    plant_id: int,
    payload: WateringCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    plant = _get_own_plant(plant_id, db, user)

    watering = Watering(plant_id=plant.id, **payload.model_dump())
    db.add(watering)

    # Обновляем дату последнего полива у растения
    if plant.last_watered_at is None or payload.watered_at > plant.last_watered_at:
        plant.last_watered_at = payload.watered_at

    db.commit()
    db.refresh(watering)
    return watering


@router.delete("/waterings/{watering_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_watering(
    watering_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Проверка владельца через JOIN
    watering = db.scalar(
        select(Watering)
        .join(Plant, Watering.plant_id == Plant.id)
        .where(Watering.id == watering_id, Plant.owner_id == user.id)
    )
    if watering is None:
        raise HTTPException(status_code=404, detail="Watering not found")
    db.delete(watering)
    db.commit()