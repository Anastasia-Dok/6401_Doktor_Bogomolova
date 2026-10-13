from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=list[schemas.SubscriptionOut])
def read_subscriptions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Подписки текущего пользователя."""
    return crud.get_subscriptions(db, user_id=current_user.id)


@router.post("/", response_model=schemas.SubscriptionOut, status_code=status.HTTP_201_CREATED)
def create_subscription(
    sub: schemas.SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Оформить подписку."""
    return crud.create_subscription(db, sub=sub, user_id=current_user.id)


@router.delete("/{sub_id}", response_model=schemas.SubscriptionOut)
def delete_subscription(
    sub_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Отменить подписку."""
    sub = crud.get_subscription(db, sub_id=sub_id)
    if not sub or sub.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
    return crud.delete_subscription(db, sub_id=sub_id)