from lionfuncs import copy


def prepare_fields(
    exclude_fields: list | dict | None = None,
    include_fields: list | dict | None = None,
    **kwargs,
):
    kwargs = copy(kwargs)

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

    return {k: (v.annotation, v) for k, v in kwargs.items()}
