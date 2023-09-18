from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import copy
from typing import Union


def is_url_valid(url: str) -> bool:
    validate = URLValidator()
    try:
        validate(url)
        return True
    except ValidationError:
        return False


def format_wide_number(number: Union[int, str], char_seperator: str) -> str:
    """
    Returns formatted string of passed number
    Example: input: 12345678, ' ' -> output: "12 345 678"
    Example: input: "12345678", ' ' -> output: "12 345 678"
    """
    if len(char_seperator) != 1:
        raise ValueError("Seperator must be a single character")

    number = str(number)
    if len(number) <= 3:
        return number
    reversed_numbers = list(number[::-1])
    reversed_numbers_copy = copy.copy(reversed_numbers)
    insert_counter = 0
    for i, _ in enumerate(reversed_numbers):
        if i % 3 == 0 and i != 0:
            reversed_numbers_copy.insert(i + insert_counter, char_seperator)
            insert_counter += 1
    return "".join(reversed_numbers_copy[::-1])
