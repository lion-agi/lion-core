from typing import Any, Type
from lion_core.generic.utils import change_dict_key


llama_meta_fields = [
    "id_",
    "embedding",
    "excluded_embed_metadata_keys",
    "excluded_llm_metadata_keys",
    "relationships",
    "start_char_idx",
    "end_char_idx",
    "class_name",
    "text_template",
    "metadata_template",
    "metadata_seperator",
]


class LlamaIndexComponentMixin:

    @classmethod
    def _from_llama_index(cls, obj: Any):
        """Create a Component instance from a LlamaIndex object."""
        dict_ = obj.to_dict()

        change_dict_key(dict_, "text", "content")
        metadata = dict_.pop("metadata", {})

        for field in llama_meta_fields:
            metadata[field] = dict_.pop(field, None)

        change_dict_key(metadata, "class_name", "llama_index_class")
        change_dict_key(metadata, "id_", "llama_index_id")
        change_dict_key(metadata, "relationships", "llama_index_relationships")

        dict_["metadata"] = metadata
        return cls.from_obj(dict_)
