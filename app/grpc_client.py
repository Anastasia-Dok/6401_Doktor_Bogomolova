"""Клиент для вызова gRPC Analytics Service."""
import grpc

from grpc_service.generated import analytics_pb2, analytics_pb2_grpc
from app.config import settings


def _get_stub():
    channel = grpc.insecure_channel(f"{settings.grpc_host}:{settings.grpc_port}")
    return analytics_pb2_grpc.AnalyticsServiceStub(channel)


def get_summary() -> dict:
    print("[FastAPI → gRPC] GetSummary")
    stub = _get_stub()
    response = stub.GetSummary(analytics_pb2.Empty())
    print(f"[gRPC → FastAPI] users={response.users}, notes={response.notes}")
    return {
        "users": response.users,
        "lists": response.lists,
        "notes": response.notes,
        "subscriptions": response.subscriptions,
    }


def get_top_lists(limit: int = 5) -> list[dict]:
    print(f"[FastAPI → gRPC] GetTopLists(limit={limit})")
    stub = _get_stub()
    response = stub.GetTopLists(analytics_pb2.TopListsRequest(limit=limit))
    print(f"[gRPC → FastAPI] получено {len(response.lists)} списков")
    return [
        {
            "list_id": x.list_id,
            "title": x.title,
            "notes_count": x.notes_count,
            "subscribers_count": x.subscribers_count,
        }
        for x in response.lists
    ]


def get_top_users(limit: int = 5) -> list[dict]:
    print(f"[FastAPI → gRPC] GetTopUsers(limit={limit})")
    stub = _get_stub()
    response = stub.GetTopUsers(analytics_pb2.TopUsersRequest(limit=limit))
    return [
        {
            "user_id": u.user_id,
            "username": u.username,
            "email": u.email,
            "notes_count": u.notes_count,
        }
        for u in response.users
    ]


def get_top_authors(limit: int = 5) -> list[dict]:
    print(f"[FastAPI → gRPC] GetTopAuthors(limit={limit})")
    stub = _get_stub()
    response = stub.GetTopAuthors(analytics_pb2.TopAuthorsRequest(limit=limit))
    return [{"author": a.author, "mentions": a.mentions} for a in response.authors]