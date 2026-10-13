from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.dependencies import get_db, get_current_user, require_admin

# Чтение доступно любому аутентифицированному пользователю
router = APIRouter(
    prefix="/lists", 
    tags=["lists"],
    dependencies=[Depends(get_current_user)],
    )

# Изменение доступно только админу
admin_router = APIRouter(
    prefix="/lists",
    tags=["lists (admin)"],
    dependencies=[Depends(require_admin)],
)

@router.get("/", response_model=list[schemas.ListOut])
def read_lists(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)):
    """Список доступных списков."""
    return crud.get_lists(db, skip=skip, limit=limit)


@router.get("/{list_id}", response_model=schemas.ListOut)
def read_list(
    list_id: int,
    db: Session = Depends(get_db)):
    return crud.get_list(db, list_id=list_id)

@admin_router.post("/", response_model=schemas.ListOut, status_code=status.HTTP_201_CREATED)
def create_list(
    list_data: schemas.ListCreate, 
    db: Session = Depends(get_db)):
    return crud.create_list(db, list_data=list_data)


@admin_router.patch("/{list_id}", response_model=schemas.ListOut)
def update_list(
    list_id: int, 
    list_update: schemas.ListCreate, 
    db: Session = Depends(get_db)
):
    return crud.update_list(db, list_id=list_id, list_update=list_update)

@admin_router.delete("/{list_id}", response_model=schemas.ListOut)
def delete_list(
    list_id: int, 
    db: Session = Depends(get_db)):
    return crud.delete_list(db, list_id=list_id)