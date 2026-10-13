from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=list[schemas.ListOut])
def read_subscriptions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Списки, на которые подписан текущий пользователь."""
    return crud.get_user_subscriptions(db, user_id=current_user.user_id)


@router.post("/", response_model=schemas.SubscriptionOut, status_code=status.HTTP_201_CREATED)
def create_subscription(
    sub: schemas.SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Оформить подписку."""
    try:
        return crud.create_subscription(
            db, user_id=current_user.user_id, list_id=sub.list_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(
    list_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Отписаться от списка list_id."""
    deleted = crud.delete_subscription(
        db, user_id=current_user.user_id, list_id=list_id
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )
    return None