from datetime import timezone

from pydantic import BaseModel


class LionUndefined:
    def __init__(self):
        self.undefined = True

    def __bool__(self):
        return False

    def __deepcopy__(self, memo):
        # Ensure LN_UNDEFINED is universal
        return self

    def __repr__(self):
        return "LN_UNDEFINED"

    __slots__ = ["undefined"]


LN_UNDEFINED = LionUndefined()


class SchemaModel(BaseModel):

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def from_dict(cls, **data):
        return cls(**data)


class LionIDConfig(SchemaModel):
    n: int = 42
    random_hyphen: bool = True
    num_hyphens: int = 4
    hyphen_start_index: int = 6
    hyphen_end_index: int = -6
    prefix: str = "ln"
    postfix: str = ""


class RetryConfig(SchemaModel):
    num_retries: int = 3
    initial_delay: int = 0
    retry_delay: int = 1
    backoff_factor: int = 2
    retry_default: str = LN_UNDEFINED
    retry_timeout: int = 180
    retry_timing: bool = False
    verbose_retry: bool = True
    error_msg: str = None
    error_map: dict = None


LION_ID_CONFIG = LionIDConfig().to_dict()

BASE_LION_FIELDS = {
    "ln_id",
    "timestamp",
    "metadata",
    "extra_fields",
    "content",
    "created",
    "embedding",
}

TIME_CONFIG = {
    "tz": timezone.utc,
}


SERILIATION_CONFIG = {
    "mode": "python",
    "include": None,
    "exclude": None,
    "context": None,
    "by_alias": False,
    "exclude_unset": False,
    "exclude_defaults": False,
    "exclude_none": False,
    "round_trip": False,
    "warnings": True,
    "serialize_as_any": False,
}


# File: lion_core/setting.py
