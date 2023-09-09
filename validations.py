from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from typing import Union


def is_url_valid(url: str) -> bool:
    validate = URLValidator()
    try:
        validate(url)
        return True
    except ValidationError:
        return False


def is_play_func_valid(url: Union[str, None],
                       if_previous_was_skipped: bool) -> bool:
    if if_previous_was_skipped and url:
        return False
    return True
