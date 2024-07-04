from pydantic import BaseModel


LION_ID_CONFIG = {
    "n": 28,
    "random_hyphen": True,
    "num_hyphens": 4,
    "hyphen_start_index": 6,
    "hyphen_end_index": 24,
}


BASE_LION_FIELDS = [
    "ln_id",
    "timestamp",
    "metadata",
    "extra_fields",
    "content",
    "created",
    "embedding",
]
