"""Модуль для генерации шорт кодов (случайно сгенерированных строк)."""

from secrets import choice

CHARSET = "23456789abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ"


def generate_short_code(length: int = 6) -> str:
    """
    Генерирует шорт код (строку, состоящую из случайных букв и цифр).

    Args:
        length (int): Длина генерируемой строки (по умолчанию - 6).

    Returns:
        str: Шорт код (случайно сгенерированная строка).

    Raises:
        ValueError: Если переданная длина генерируемой строки не является натуральным числом.
    """
    if length < 1 or not isinstance(length, int):
        raise ValueError("Длина генерируемой строки должна быть натуральным числом (от 1 и более)")

    generated_short_code = "".join(choice(CHARSET) for _ in range(length))

    return generated_short_code
