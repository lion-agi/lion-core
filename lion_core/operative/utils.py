import re

from lionfuncs import copy, md_to_json, to_dict
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo


def parse_action_request(content: str) -> list[dict]:

    json_blocks = md_to_json(
        str_to_parse=content,
        as_jsonl=True,
        suppress=True,
    )

    if not json_blocks:
        pattern2 = r"```python\s*(.*?)\s*```"
        _d = re.findall(pattern2, content, re.DOTALL)
        json_blocks = [
            to_dict(match, fuzzy_parse=True, suppress=True) for match in _d
        ]
        json_blocks = [i for i in json_blocks if i]

    out = []

    for i in json_blocks:
        j = {}
        if isinstance(i, dict):
            for k, v in i.items():
                k = (
                    k.replace("action_", "")
                    .replace("recipient_", "")
                    .replace("s", "")
                )
                if k in ["name", "function", "recipient"]:
                    j["function"] = v
                elif k in ["parameter", "argument", "arg"]:
                    j["arguments"] = to_dict(
                        v, str_type="json", fuzzy_parse=True, suppress=True
                    )
            if (
                j
                and all(key in j for key in ["function", "arguments"])
                and j["arguments"]
            ):
                out.append(j)

    return out


def prepare_fields(
    cls,
    exclude_fields: list | dict | None = None,
    include_fields: list | dict | None = None,
    field_descriptions: dict = None,
    use_base_kwargs: bool = False,
    operative_model=None,
    use_all_fields: bool = True,
    **kwargs,
):
    kwargs = copy(kwargs)

    operative_model = operative_model or BaseModel
    if (
        use_all_fields
        and hasattr(operative_model, "all_fields")
        and isinstance(operative_model, BaseModel)
    ):
        kwargs.update(copy(cls.all_fields))
    else:
        kwargs.update(copy(cls.model_fields))

    if exclude_fields:
        exclude_fields = (
            list(exclude_fields.keys())
            if isinstance(exclude_fields, dict)
            else exclude_fields
        )

    if include_fields:
        include_fields = (
            list(include_fields.keys())
            if isinstance(include_fields, dict)
            else include_fields
        )

    if exclude_fields and include_fields:
        for i in include_fields:
            if i in exclude_fields:
                raise ValueError(
                    f"Field {i} is repeated. Operation include "
                    "fields and exclude fields cannot have common elements."
                )

    if exclude_fields:
        for i in exclude_fields:
            kwargs.pop(i, None)

    if include_fields:
        for i in list(kwargs.keys()):
            if i not in include_fields:
                kwargs.pop(i, None)

    fields = {k: (v.annotation, v) for k, v in kwargs.items()}

    if field_descriptions:
        for field_name, description in field_descriptions.items():
            if field_name in fields:
                field_info = fields[field_name]
                if isinstance(field_info, tuple):
                    fields[field_name] = (
                        field_info[0],
                        Field(..., description=description),
                    )
                elif isinstance(field_info, FieldInfo):
                    fields[field_name] = field_info.model_copy(
                        update={"description": description}
                    )

    # Prepare class attributes
    class_kwargs = {}
    if use_base_kwargs:
        class_kwargs.update(
            {
                k: getattr(operative_model, k)
                for k in operative_model.__dict__
                if not k.startswith("__")
            }
        )

    class_kwargs = {k: v for k, v in class_kwargs.items() if k in fields}

    name = None
    if hasattr(operative_model, "class_name"):
        if callable(operative_model.class_name):
            name = operative_model.class_name()
        else:
            name = operative_model.class_name
    else:
        name = operative_model.__name__
        if name == "BaseModel":
            name = cls.__name__

    return fields, class_kwargs, name
