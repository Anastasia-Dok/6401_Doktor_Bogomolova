"""gRPC Analytics Service — сервер."""
import logging
from concurrent import futures

import grpc

from grpc_service.generated import analytics_pb2, analytics_pb2_grpc
from grpc_service.db_access import (
    get_summary_data,
    get_top_lists_data,
    get_top_users_data,
    get_top_authors_data,
)


class AnalyticsServicer(analytics_pb2_grpc.AnalyticsServiceServicer):

    def GetSummary(self, request, context):
        print("[gRPC] GetSummary вызван")
        data = get_summary_data()
        print(f"[gRPC] Ответ: {data}")
        return analytics_pb2.Summary(**data)

    def GetTopLists(self, request, context):
        limit = request.limit or 5
        print(f"[gRPC] GetTopLists(limit={limit})")
        rows = get_top_lists_data(limit)
        print(f"[gRPC] Найдено списков: {len(rows)}")
        return analytics_pb2.TopListsResponse(
            lists=[
                analytics_pb2.ListStat(**row)
                for row in rows
            ]
        )

    def GetTopUsers(self, request, context):
        limit = request.limit or 5
        print(f"[gRPC] GetTopUsers(limit={limit})")
        rows = get_top_users_data(limit)
        print(f"[gRPC] Найдено пользователей: {len(rows)}")
        return analytics_pb2.TopUsersResponse(
            users=[analytics_pb2.UserStat(**row) for row in rows]
        )

    def GetTopAuthors(self, request, context):
        limit = request.limit or 5
        print(f"[gRPC] GetTopAuthors(limit={limit})")
        rows = get_top_authors_data(limit)
        print(f"[gRPC] Найдено авторов: {len(rows)}")
        return analytics_pb2.TopAuthorsResponse(
            authors=[analytics_pb2.AuthorStat(**row) for row in rows]
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    analytics_pb2_grpc.add_AnalyticsServiceServicer_to_server(
        AnalyticsServicer(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    print("=" * 50)
    print("gRPC Analytics Service запущен на :50051")
    print("=" * 50)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    serve()