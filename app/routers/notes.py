from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/notes", tags=["notes"])

ADMIN_ROLE_NAME = "admin" 

def _ensure_owner_or_admin(note_user_id: int, current_user) -> None:
    if note_user_id != current_user.user_id and current_user.role.name != ADMIN_ROLE_NAME:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@router.get("/", response_model=list[schemas.NoteOut])
def read_notes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user),
):
    notes = crud.get_notes_by_user(db, user_id=current_user.user_id)
    return notes[skip : skip + limit]


@router.post("/", response_model=schemas.NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(
    note: schemas.NoteCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user),
):
    return crud.create_note(
        db,
        user_id=current_user.user_id,
        list_id=note.list_id,
        title=note.title,
        author=note.author,
        review=note.review,
    )


@router.patch("/{note_id}", response_model=schemas.NoteOut)
def update_note(
    note_id: int,
    note_update: schemas.NoteUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    note = crud.get_note(db, note_id=note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    _ensure_owner_or_admin(note.user_id, current_user)
    data = note_update.model_dump(exclude_unset=True)
    updated = crud.update_note(db, note_id=note_id, **data)
    return updated



@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Удалить заметку. Только автор или админ."""
    note = crud.get_note(db, note_id=note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    _ensure_owner_or_admin(note.user_id, current_user)
    crud.delete_note(db, note_id=note_id)
    return None