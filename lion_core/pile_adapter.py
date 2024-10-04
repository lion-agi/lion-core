import json
from pathlib import Path
from typing import Any, Protocol, TypeVar, runtime_checkable

from lionfuncs import save_to_file, to_dict

T = TypeVar("T")


@runtime_checkable
class Dumper(Protocol):
    """save to file"""

    default_directory: Path = Path(".") / "data" / "pile_dump"
    default_filename: str = "unnamed_pile_dump"
    obj_key: str

    @classmethod
    def dump_to(
        cls,
        subj: T,
        /,
        **kwargs: Any,
    ):
        raise NotImplementedError


class JsonDumper(Dumper):

    default_directory: Path = Path(".") / "data" / "pile_dump" / "json"
    default_filename: str = "unnamed_pile_dump_json"
    obj_key = ".json"

    @classmethod
    def dump_to(
        cls,
        subj: T,
        /,
        **kwargs,
    ):
        """
        kwargs for save to file
        """
        str_ = json.dumps(subj.to_dict())
        save_to_file(
            str_,
            extension=cls.obj_key,
            **kwargs,
        )


@runtime_checkable
class Loader(Protocol):
    """load from source (file or other)"""

    obj_key: str

    @classmethod
    def load_from(
        cls,
        obj: Any,
        **kwargs: Any,
    ):
        raise NotImplementedError


class JsonLoader(Loader):

    obj_key = "json"

    @classmethod
    def load_from(
        cls,
        obj: str,
        recursive: bool = False,
        recursive_python_only: bool = True,
        **kwargs: Any,
    ) -> dict:

        return to_dict(
            obj,
            recursive=recursive,
            recursive_python_only=recursive_python_only,
            **kwargs,
        )


class AdapterRegistry:

    _loaders: dict[str, Loader] = {}
    _dumpers: dict[str, Dumper] = {}

    @classmethod
    def register(cls, adapter: Dumper | Loader, /) -> None:
        if isinstance(adapter, Dumper):
            if not hasattr(adapter, "dump_to"):
                raise ValueError(
                    "The <Dumper> protocol requires the method "
                    "<dump_to> to be implemented. "
                )
            cls._dumpers[adapter.obj_key] = adapter
        elif isinstance(adapter, Loader):
            if not hasattr(adapter, "load_from"):
                raise ValueError(
                    "The <Loader> protocol requires the method "
                    "<load_from> to be implemented. "
                )
            cls._loaders[adapter.obj_key] = adapter
        else:
            raise ValueError(
                "The adapter needs to be a subclass of the <Dumper> or"
                "<Loader> protocol."
            )

    @classmethod
    def all_keys(cls) -> dict[str, list[str]]:
        return {
            "loader": cls.list_loader_keys(),
            "dumper": cls.list_dumper_keys(),
        }

    @classmethod
    def list_loader_keys(cls) -> list[str]:
        return list(cls._loaders.keys())

    @classmethod
    def list_dumper_keys(cls) -> list[str]:
        return list(cls._dumpers.keys())

    @classmethod
    def load(cls, obj, obj_key, /, **kwargs) -> dict | list[dict]:
        return cls._loaders[obj_key].load_from(obj, **kwargs)

    @classmethod
    def dump(cls, subj, obj_key, /, **kwargs):
        cls._dumpers[obj_key].dump_to(subj, **kwargs)
