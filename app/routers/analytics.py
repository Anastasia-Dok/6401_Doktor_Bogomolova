from fastapi import APIRouter, Depends

from app.dependencies import require_admin
from app import grpc_client
from app.schemas import SummaryOut, TopListsOut, TopUsersOut, TopAuthorsOut

router = APIRouter(prefix="/admin/analytics", tags=["analytics"])


@router.get("/summary", response_model=SummaryOut)
def summary(admin=Depends(require_admin)):
    return grpc_client.get_summary()


@router.get("/top-lists", response_model=list[TopListsOut])
def top_lists(limit: int = 5, admin=Depends(require_admin)):
    return grpc_client.get_top_lists(limit)


@router.get("/top-users", response_model=list[TopUsersOut])
def top_users(limit: int = 5, admin=Depends(require_admin)):
    return grpc_client.get_top_users(limit)


@router.get("/top-authors", response_model=list[TopAuthorsOut])
def top_authors(limit: int = 5, admin=Depends(require_admin)):
    return grpc_client.get_top_authors(limit)