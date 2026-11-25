"""Консольное приложение для заметок.

У каждой заметки есть название и текст. По умолчанию список выводится
от самой короткой заметки к самой длинной. Длина считается по тексту.
"""

from __future__ import annotations


def _clean(value: str) -> str:
    return value.strip()


def find_note(notes: list[dict], title: str) -> dict | None:
    """Ищет заметку по названию без учёта регистра и лишних пробелов."""
    normalized = _clean(title).casefold()
    if not normalized:
        return None
    for note in notes:
        if note["title"].casefold() == normalized:
            return note
    return None


def create_note(notes: list[dict], title: str, text: str) -> None:
    """Создаёт заметку с названием и текстом.

    Raises:
        ValueError: название или текст пустые, либо такое название уже есть.
    """
    title = _clean(title)
    text = _clean(text)
    if not title:
        raise ValueError("Название заметки не может быть пустым.")
    if not text:
        raise ValueError("Текст заметки не может быть пустым.")
    if find_note(notes, title) is not None:
        raise ValueError(f"Заметка с названием «{title}» уже существует.")
    notes.append({"title": title, "text": text})


def delete_note(notes: list[dict], title: str) -> None:
    """Удаляет заметку по названию.

    Raises:
        ValueError: название пустое или заметка не найдена.
    """
    title = _clean(title)
    if not title:
        raise ValueError("Укажите название заметки, которую нужно удалить.")
    note = find_note(notes, title)
    if note is None:
        raise ValueError(f"Заметка «{title}» не найдена.")
    notes.remove(note)


def edit_note(
    notes: list[dict],
    title: str,
    new_title: str | None = None,
    new_text: str | None = None,
) -> None:
    """Меняет название и/или текст существующей заметки.

    Пустая строка означает, что это поле остаётся прежним.

    Raises:
        ValueError: заметка не найдена или новые данные некорректны.
    """
    title = _clean(title)
    if not title:
        raise ValueError("Укажите название заметки, которую нужно изменить.")
    note = find_note(notes, title)
    if note is None:
        raise ValueError(f"Заметка «{title}» не найдена.")

    updated_title = _clean(new_title) if new_title is not None else ""
    updated_text = _clean(new_text) if new_text is not None else ""
    if not updated_title and not updated_text:
        raise ValueError("Нечего изменять: укажите новое название или новый текст.")

    if updated_title:
        same_note = updated_title.casefold() == note["title"].casefold()
        if not same_note and find_note(notes, updated_title) is not None:
            raise ValueError(
                f"Заметка с названием «{updated_title}» уже существует."
            )
        note["title"] = updated_title
    if updated_text:
        note["text"] = updated_text


def sort_notes(notes: list[dict], *, longest_first: bool = False) -> list[dict]:
    """Возвращает копию списка заметок, упорядоченную по длине текста.

    По умолчанию порядок — от самой короткой к самой длинной.
    Если longest_first=True, порядок обратный: от самой длинной к самой короткой.
    При равной длине заметки идут по названию.
    """
    return sorted(
        notes,
        key=lambda note: (len(note["text"]), note["title"].casefold()),
        reverse=longest_first,
    )


def format_notes(notes: list[dict], *, longest_first: bool = False) -> str:
    """Собирает текст списка заметок в выбранном порядке."""
    ordered = sort_notes(notes, longest_first=longest_first)
    if not ordered:
        return "Заметок пока нет."

    direction = (
        "от самой длинной к самой короткой"
        if longest_first
        else "от самой короткой к самой длинной"
    )
    lines = [f"Заметки ({direction}):", ""]
    for index, note in enumerate(ordered, start=1):
        lines.append(f"{index}. {note['title']} — {len(note['text'])} симв.")
        lines.append(note["text"])
        lines.append("")
    return "\n".join(lines).rstrip()


MENU = """
Приложение «Заметки»
1 — создать заметку
2 — удалить заметку
3 — редактировать заметку
4 — показать заметки (от короткой к длинной)
5 — показать заметки (от длинной к короткой)
0 — выход
""".strip()


def _read_line(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError as exc:
        raise KeyboardInterrupt from exc


def _ask_yes_no(prompt: str) -> bool:
    answer = _clean(_read_line(prompt)).casefold()
    if answer in {"д", "да", "y", "yes"}:
        return True
    if answer in {"н", "нет", "n", "no"}:
        return False
    raise ValueError("Введите «да» или «нет».")


def _print_default_notes(notes: list[dict]) -> None:
    print()
    print(format_notes(notes, longest_first=False))


def run_app(notes: list[dict] | None = None) -> None:
    """Управляет работой приложения: меню, ввод пользователя и операции."""
    if notes is None:
        notes = []

    print("Добро пожаловать в приложение для заметок.")
    print("По умолчанию заметки показываются от самой короткой к самой длинной.")
    _print_default_notes(notes)

    while True:
        print()
        print(MENU)
        try:
            choice = _clean(_read_line("Выберите действие: "))
            if choice == "0":
                print("До свидания.")
                return
            if choice == "1":
                title = _read_line("Название: ")
                text = _read_line("Текст: ")
                create_note(notes, title, text)
                print(f"Заметка «{_clean(title)}» создана.")
                _print_default_notes(notes)
            elif choice == "2":
                title = _read_line("Название заметки для удаления: ")
                note = find_note(notes, title)
                if note is None:
                    delete_note(notes, title)
                elif _ask_yes_no(f"Удалить заметку «{note['title']}»? (да/нет): "):
                    delete_note(notes, note["title"])
                    print(f"Заметка «{note['title']}» удалена.")
                    _print_default_notes(notes)
                else:
                    print("Удаление отменено.")
            elif choice == "3":
                title = _read_line("Название заметки для редактирования: ")
                print("Оставьте поле пустым, если его менять не нужно.")
                new_title = _read_line("Новое название: ")
                new_text = _read_line("Новый текст: ")
                edit_note(notes, title, new_title, new_text)
                print("Заметка обновлена.")
                _print_default_notes(notes)
            elif choice == "4":
                _print_default_notes(notes)
            elif choice == "5":
                print()
                print(format_notes(notes, longest_first=True))
            else:
                print("Неизвестная команда. Введите число от 0 до 5.")
        except ValueError as error:
            print(f"Ошибка: {error}")
        except KeyboardInterrupt:
            print("\nРабота приложения завершена.")
            return


if __name__ == "__main__":
    run_app()
