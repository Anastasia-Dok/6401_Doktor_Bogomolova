from crud import (
    get_role, update_role, delete_role, get_all_users_with_role,
    get_user_by_id, get_user_by_email, get_user_by_username, update_user, delete_user,
    get_list, get_all_lists, update_list, delete_list,
    search_lists_by_title, get_list_with_notes, get_list_with_notes_and_authors,
    get_note, update_note, delete_note, get_notes_by_list, get_notes_by_user, get_note_with_author,
    get_subscription, delete_subscription, get_user_subscriptions, get_list_subscribers,
)

def section(title: str) -> None:
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def main() -> None:

    # ---------- Role ----------
    section("ROLE")
    role = get_role(1)
    print(f"  get_role(1) -> {role}")

    updated = update_role(1, "superadmin")
    print(f"  update_role(1, 'superadmin') -> {updated}")

    # Попытка удалить несуществующую роль
    deleted = delete_role(999)
    print(f"  delete_role(999) -> {deleted}")

    # Все пользователи с ролями
    users_with_roles = get_all_users_with_role()
    print(f"  get_all_users_with_role() -> {len(users_with_roles)} пользователей")
    for u in users_with_roles:
        print(f"    {u.user_id}: {u.username} ({u.role.name})")

    # ---------- User ----------
    section("USER")
    user = get_user_by_id(2)
    print(f"  get_user_by_id(2) -> {user}")

    user_by_email = get_user_by_email("john@example.com")
    print(f"  get_user_by_email('john@example.com') -> {user_by_email}")

    user_by_name = get_user_by_username("maria")
    print(f"  get_user_by_username('maria') -> {user_by_name}")

    updated_user = update_user(2, email="john.new@example.com")
    print(f"  update_user(2, email='john.new@example.com') -> {updated_user}")

    deleted_user = delete_user(999)
    print(f"  delete_user(999) -> {deleted_user}")

    # ---------- Lists ----------
    section("LISTS")
    lst = get_list(1)
    print(f"  get_list(1) -> {lst}")

    all_lists = get_all_lists()
    print(f"  get_all_lists() -> {[l.title for l in all_lists]}")

    updated_list = update_list(1, "Фильмы и сериалы")
    print(f"  update_list(1, 'Фильмы и сериалы') -> {updated_list}")

    deleted_list = delete_list(999)
    print(f"  delete_list(999) -> {deleted_list}")

    search_result = search_lists_by_title("и")
    print(f"  search_lists_by_title('и') -> {[l.title for l in search_result]}")

    list_with_notes = get_list_with_notes(1)
    print(f"  get_list_with_notes(1) -> список '{list_with_notes.title}', заметок: {len(list_with_notes.notes)}")

    list_with_authors = get_list_with_notes_and_authors(1)
    if list_with_authors and list_with_authors.notes:
        first_note = list_with_authors.notes[0]
        print(f"  get_list_with_notes_and_authors(1) -> первая заметка: '{first_note.title}' (автор: {first_note.user.username})")
    else:
        print("  get_list_with_notes_and_authors(1) -> нет заметок")

    # ---------- Note ----------
    section("NOTE")
    note = get_note(1)
    print(f"  get_note(1) -> {note}")

    updated_note = update_note(1, review="Обновлённый отзыв")
    print(f"  update_note(1, review='Обновлённый отзыв') -> {updated_note}")

    # Удалим заметку с id=1 (безопасно, т.к. на неё никто не ссылается)
    deleted_note = delete_note(1)
    print(f"  delete_note(1) -> {deleted_note}")

    notes_by_list = get_notes_by_list(1)
    print(f"  get_notes_by_list(1) -> {len(notes_by_list)} заметок")

    notes_by_user = get_notes_by_user(2)
    print(f"  get_notes_by_user(2) -> {len(notes_by_user)} заметок")

    note_with_author = get_note_with_author(2)
    if note_with_author:
        print(f"  get_note_with_author(2) -> '{note_with_author.title}', автор: {note_with_author.user.username}")
    else:
        print("  get_note_with_author(2) -> заметка не найдена")

    # ---------- Subscription ----------
    section("SUBSCRIPTION")
    sub = get_subscription(2, 2)  # john подписан на music
    print(f"  get_subscription(2, 2) -> {sub}")

    # Удалим подписку (безопасно)
    deleted_sub = delete_subscription(2, 2)
    print(f"  delete_subscription(2, 2) -> {deleted_sub}")

    user_subs = get_user_subscriptions(2)
    print(f"  get_user_subscriptions(2) -> {[l.title for l in user_subs]}")

    list_subs = get_list_subscribers(1)  # список "Фильмы"
    print(f"  get_list_subscribers(1) -> {[u.username for u in list_subs]}")

if __name__ == "__main__":
    main()