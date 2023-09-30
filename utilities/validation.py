from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


def is_url_valid(url: str) -> bool:
    validate = URLValidator()
    try:
        validate(url)
        return True
    except ValidationError:
        return False
