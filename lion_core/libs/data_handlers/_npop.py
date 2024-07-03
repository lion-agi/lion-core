from lion_core.libs.data_handlers._to_list import to_list


def npop(input_, /, indices, default=None):
    if not indices:
        raise ValueError("Indices list cannot be empty")

    indices = to_list(indices)

    current = input_
    for key in indices[:-1]:
        if isinstance(current, dict):
            if current.get(key):
                current = current[key]
            else:
                raise KeyError(f"{key} is not found in {current}")
        elif isinstance(current, list) and isinstance(key, int):
            if key >= len(current):
                raise KeyError(f"{key} exceeds the length of the list {current}")
            elif key < 0:
                raise ValueError(f"list index cannot be negative")
            current = current[key]

    last_key = indices[-1]
    try:
        return current.pop(last_key, )
    except Exception as e:
        if default:
            return default
        else:
            raise KeyError(f"Invalid npop. Error: {e}")


# Path: lion_core/libs/data_handlers/_npop.py