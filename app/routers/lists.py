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
    db: Session = Depends(get_db)):
    """Список доступных списков."""
    return crud.get_all_lists(db)


@router.get("/{list_id}", response_model=schemas.ListOut)
def read_list(
    list_id: int,
    db: Session = Depends(get_db)):
    lst = crud.get_list(db, list_id=list_id)
    if not lst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")
    return lst

@admin_router.post("/", response_model=schemas.ListOut, status_code=status.HTTP_201_CREATED)
def create_list(
    list_data: schemas.ListCreate, 
    db: Session = Depends(get_db)):
    return crud.create_list(db, title=list_data.title)


@admin_router.patch("/{list_id}", response_model=schemas.ListOut)
def update_list(
    list_id: int, 
    list_update: schemas.ListCreate, 
    db: Session = Depends(get_db)
):
    lst = crud.update_list(db, list_id=list_id, new_title=list_update.title)
    if not lst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")
    return lst

@admin_router.delete("/{list_id}", response_model=schemas.ListOut)
def delete_list(
    list_id: int, 
    db: Session = Depends(get_db)):
    ok = crud.delete_list(db, list_id=list_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")
    return None