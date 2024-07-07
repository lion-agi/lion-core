from pydantic import Field


def field(*args, **kwargs):
    return Field(*args, **kwargs)
