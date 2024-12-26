from re import match


def str_like_true(x: str):
    return bool(match(r"^[tT]", x))
