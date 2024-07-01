def change_dict_key(dict_, old_key: str, new_key: str) -> None:
    if old_key in dict_:
        dict_[new_key] = dict_.pop(old_key)
