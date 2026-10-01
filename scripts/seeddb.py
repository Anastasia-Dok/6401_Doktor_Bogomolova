from db import init_db
from crud import (
    create_role,
    create_user,
    create_list,
    create_note,
    create_subscription,
)


def section(title: str) -> None:
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main() -> None:
    section("ИНИЦИАЛИЗАЦИЯ БД")
    init_db()
    print(" Таблицы созданы!")

    # ---------- 1. Роли ----------
    section("1. РОЛИ")
    admin_role = create_role("admin")
    user_role = create_role("user")
    print(f"  [+] role {admin_role.role_id}: {admin_role.name!r}")
    print(f"  [+] role {user_role.role_id}: {user_role.name!r}")

    # ---------- 2. Пользователи ----------

    section("2. ПОЛЬЗОВАТЕЛИ")
    admin = create_user("admin", "admin@example.com", "admin_secret", admin_role.role_id)
    john = create_user("john", "john@example.com", "john_secret", user_role.role_id)
    maria = create_user("maria", "maria@example.com", "maria_secret", user_role.role_id)
    alex = create_user("alex", "alex@example.com", "alex_secret", user_role.role_id)
    for u in (admin, john, maria, alex):
        print(f"  [+] user {u.user_id}: {u.username!r} <{u.email}>")

    # ---------- 3. Тематические списки ----------
   
    section("3. ТЕМАТИЧЕСКИЕ СПИСКИ")
    films = create_list("Фильмы")
    music = create_list("Музыка")
    books = create_list("Книги")
    games = create_list("Игры")
    for lst in (films, music, books, games):
        print(f"  [+] list {lst.list_id}: {lst.title!r}")

    # ---------- 4. Записи ----------

    section("4. ЗАПИСИ")

    print("\n  -- Фильмы --")
    for uid, title, author, review in [
        (john.user_id, "Интерстеллар", "Кристофер Нолан",
         "Один из лучших фильмов о космосе и времени."),
        (john.user_id, "Бегущий по лезвию 2049", "Дени Вильнёв",
         "Визуально безупречный фильм, продолжение классики."),
        (maria.user_id, "Паразиты", "Пон Джун Хо",
         "Острая социальная сатира, обладатель Оскара."),
        (alex.user_id, "Дюна", "Дени Вильнёв",
         "Эпичное полотно, отличная экранизация Герберта."),
    ]:
        n = create_note(uid, films.list_id, title, author, review)
        print(f"    [+] note {n.note_id}: {n.title!r} / {n.author!r}")

    print("\n  -- Музыка --")
    for uid, title, author, review in [
        (maria.user_id, "Random Access Memories", "Daft Punk",
         "Классика электроники, идеальный альбом."),
        (alex.user_id, "The Dark Side of the Moon", "Pink Floyd",
         "Легендарный альбом, слушать целиком."),
        (john.user_id, "OK Computer", "Radiohead",
         "Альбом, опередивший своё время."),
    ]:
        n = create_note(uid, music.list_id, title, author, review)
        print(f"    [+] note {n.note_id}: {n.title!r} / {n.author!r}")

    print("\n  -- Книги --")
    for uid, title, author, review in [
        (maria.user_id, "1984", "Джордж Оруэлл",
         "Антиутопия, актуальная и сегодня."),
        (alex.user_id, "Мастер и Маргарита", "Михаил Булгаков",
         "Одно из главных произведений русской литературы."),
        (john.user_id, "Дюна", "Фрэнк Герберт",
         "Классика научной фантастики."),
    ]:
        n = create_note(uid, books.list_id, title, author, review)
        print(f"    [+] note {n.note_id}: {n.title!r} / {n.author!r}")

    print("\n  -- Игры --")
    for uid, title, author, review in [
        (alex.user_id, "The Witcher 3", "CD Projekt Red",
         "Одна из лучших RPG всех времён."),
        (maria.user_id, "Hollow Knight", "Team Cherry",
         "Атмосферный метроидвания-шедевр."),
    ]:
        n = create_note(uid, games.list_id, title, author, review)
        print(f"    [+] note {n.note_id}: {n.title!r} / {n.author!r}")
   
    # ---------- 5. Подписки ----------
   
    section("5. ПОДПИСКИ")
    for uid, lid in [
        (john.user_id, music.list_id),
        (john.user_id, games.list_id),
        (maria.user_id, films.list_id),
        (maria.user_id, books.list_id),
        (alex.user_id, films.list_id),
        (alex.user_id, music.list_id),
        (alex.user_id, books.list_id),
    ]:
        create_subscription(uid, lid)
        print(f"  [+] sub user={uid} → list={lid}")


if __name__ == "__main__":
    main()