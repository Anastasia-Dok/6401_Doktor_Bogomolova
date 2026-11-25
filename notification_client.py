"""Клиент: держит WS-соединение, печатает уведомления."""
import asyncio
import pickle
import sys

import websockets


async def listen(user_id: int):
    #  Подключаемся просто по хосту и порту
    url = "ws://127.0.0.1:8001/ws" 
    print(f"[*] Подключаюсь к {url}...")
    # когда блок кода закончится, соединение будет автоматически закрыто 
    async with websockets.connect(url) as ws: # отправляет HTTP-запрос с заголовком Upgrade: websocket
        print("[*] Соединение установлено.")

        # 2. Передача данных: шлем свой ID
        auth_data = {"user_id": user_id}
        await ws.send(pickle.dumps(auth_data)) #ждём завершения рукопожатия
        print(f"[*] Отправил свой ID ({user_id}). Жду уведомления...\n")

        # 3. Читаем уведомления
        async for message in ws:
            data = pickle.loads(message)
            if data.get("type") == "notification":
                print(f" [{data['event']}] {data['text']}")

if __name__ == "__main__":
    uid = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    try:#запускает event loop и выполняет внутри него нашу асинхронную функцию listen(uid)
        asyncio.run(listen(uid))
    except KeyboardInterrupt:
        print("\n[CLIENT] Отключён")