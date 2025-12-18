"""Модуль для кодирования целого числа в строку Base62"""


BASE = 62
CHARSET = "23456789abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ"
CHARSET_MAP = {char: index for index, char in enumerate(CHARSET)}


def encode_base62(number: int) -> str:
    """
    Кодирует положительное целое число в строку Base62.

    Args:
        number (int): Целое число для кодирования. Должно быть неотрицательным.

    Returns:
        str: Закодированная строка Base62. Возвращает пустую строку, если num равно 0.

    Raises:
        ValueError: Если переданное число отрицательное.
    """

    if number < 0:
        raise ValueError("Число должно быть неотрицательным")

    if number == 0:
        return "0"

    encoded_str = ""

    while number > 0:
        char_index = number % BASE
        number = number // BASE
        encoded_str = CHARSET[char_index] + encoded_str

    return encoded_str


def decode_base62(encoded_str: str) -> int:
    """Декодирует строку Base62 обратно в целое число.

    Args:
        encoded_str (str): Строка Base62 для декодирования.

    Returns:
        int: Декодированное целочисленное значение.

    Raises:
        ValueError: Если строка содержит символы, отсутствующие в наборе допустимых символов.
    """

    number = 0

    for index, char in enumerate(encoded_str):
        pow_value = len(encoded_str) - (index + 1)
        position = CHARSET_MAP[char]
        number += position * (BASE ** pow_value)

    return number


# --- Пример использования ---

if __name__ == "__main__":
    original_num = 987654321

    # Конвертация в Base62
    encoded = encode_base62(original_num)
    print(f"Number: {original_num} -> Base62: {encoded}")

    # Конвертация обратно
    try:
        decoded_num = decode_base62(encoded)
        print(f"Base62: {encoded} -> Number: {decoded_num}")
    except ValueError as exc:
        print(exc)

    # Проверка ошибки
    try:
        decode_base62("1")
    except KeyError as exc:
        print(f"Ошибка: недопустимый символ {exc}")
