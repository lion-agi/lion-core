from typing import Any

from lion_core.setting import base_lion_fields
from lion_core.generic.utils import change_dict_key

lc_meta_fields = ["lc", "type", "id", "langchain", "lc_type", "lc_id"]


class LangChainComponentMixin:

    @classmethod
    def _from_langchain(cls, obj: Any):
        """Create a Component instance from a Langchain object."""
        dict_ = obj.to_json()
        return cls.from_obj(dict_)

    @classmethod
    def _process_langchain_dict(cls, dict_: dict) -> dict:
        """Process a dictionary containing Langchain-specific data."""
        change_dict_key(dict_, "page_content", "content")

        metadata = dict_.pop("metadata", {})
        metadata.update(dict_.pop("kwargs", {}))

        if not isinstance(metadata, dict):
            metadata = {"extra_meta": metadata}

        for field in base_lion_fields:
            if field in metadata:
                dict_[field] = metadata.pop(field)

        for key in list(metadata.keys()):
            if key not in lc_meta_fields:
                dict_[key] = metadata.pop(key)

        for field in lc_meta_fields:
            if field in dict_:
                metadata[field] = dict_.pop(field)

        change_dict_key(metadata, "lc", "langchain")
        change_dict_key(metadata, "type", "lc_type")
        change_dict_key(metadata, "id", "lc_id")

        extra_fields = {k: v for k, v in metadata.items() if k not in lc_meta_fields}
        metadata = {k: v for k, v in metadata.items() if k in lc_meta_fields}
        dict_["metadata"] = metadata
        dict_.update(extra_fields)

        return dict_
