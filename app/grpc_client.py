"""Клиент для вызова gRPC Analytics Service."""
import grpc

from grpc_service.generated import analytics_pb2, analytics_pb2_grpc
from app.config import settings


def _get_stub():
    #Создаёт канал (TCP-соединение) к gRPC-серверу.
    channel = grpc.insecure_channel(f"{settings.grpc_host}:{settings.grpc_port}") 
    return analytics_pb2_grpc.AnalyticsServiceStub(channel) # Создаёт клиентский stub — обёртку над каналом.


def get_summary() -> dict:
    print("[FastAPI → gRPC] GetSummary")
    stub = _get_stub() # Создаёт клиент.
    response = stub.GetSummary(analytics_pb2.Empty()) # сериализация, HTTP/2, ожидание ответа, десериализация
    print(f"[gRPC → FastAPI] users={response.users}, notes={response.notes}")
    return {
        "users": response.users,
        "lists": response.lists,
        "notes": response.notes,
        "subscriptions": response.subscriptions,
    }


def get_top_lists(limit: int = 5) -> list[dict]:
    print(f"[FastAPI → gRPC] GetTopLists(limit={limit}) — stream")
    stub = _get_stub()
    # Вызываем метод, передавая новый LimitRequest
    stream = stub.GetTopLists(analytics_pb2.LimitRequest(limit=limit))
    result = []
    for item in stream:  # Читаем из потока
        result.append({
            "list_id": item.list_id,
            "title": item.title,
            "notes_count": item.notes_count,
            "subscribers_count": item.subscribers_count,
        })
    print(f"[gRPC → FastAPI] получено {len(result)} списков (stream)")
    return result

def get_top_users(limit: int = 5) -> list[dict]:
    print(f"[FastAPI → gRPC] GetTopUsers(limit={limit}) — stream")
    stub = _get_stub()
    stream = stub.GetTopUsers(analytics_pb2.LimitRequest(limit=limit))
    
    result = []
    for item in stream:
        result.append({
            "user_id": item.user_id,
            "username": item.username,
            "email": item.email,
            "notes_count": item.notes_count,
        })
    return result

def get_top_authors(limit: int = 5) -> list[dict]:
    print(f"[FastAPI → gRPC] GetTopAuthors(limit={limit}) — stream")
    stub = _get_stub()
    stream = stub.GetTopAuthors(analytics_pb2.LimitRequest(limit=limit))
    result = []
    for i in stream:
        result.append({"author": i.author, "mentions": i.mentions})
    return result