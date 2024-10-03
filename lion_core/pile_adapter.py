import json
from pathlib import Path
from typing import Any, Literal, Protocol, TypeVar, runtime_checkable

from lionabc import Collective
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
        *,
        directory: Path | str = None,
        filename: str = None,
        timestamp: bool = True,
        **kwargs,
    ):
        """
        kwargs for save to file
        """
        str_ = json.dumps(subj.to_dict())
        save_to_file(
            str_,
            directory=directory or cls.default_directory,
            filename=filename or cls.default_filename,
            timestamp=timestamp,
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
        subj_cls: type[Collective],
        obj: Any,
        /,
        **kwargs: Any,
    ):
        raise NotImplementedError


class JsonLoader(Loader):

    obj_key = "json"

    @classmethod
    def load_from(
        cls,
        subj_cls: type[Collective],
        obj: str,
        /,
        *,
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
    def register(cls, adapter: type[Dumper] | type[Loader], /) -> None:
        err_msg = ""

        if not isinstance(adapter, type(Dumper)) and not isinstance(
            adapter, type(Loader)
        ):
            err_msg += (
                "In order to register the adapter, it needs to be a "
                "subclass of the <Dumper> or <Loader> protocol. "
            )
            if isinstance(adapter, Dumper) or isinstance(adapter, Loader):
                err_msg += (
                    f"The converter value received <{adapter.obj_key}> "
                    "is an instance. Did you mean to register the class?"
                )
            raise ValueError(err_msg)

        if isinstance(adapter, type(Loader)):
            cls._loaders[adapter.obj_key] = adapter()
        else:
            cls._dumpers[adapter.obj_key] = adapter()

    @classmethod
    def list_loader_keys(cls) -> list[str]:
        return list(cls._loaders.keys())

    @classmethod
    def list_dumper_keys(cls) -> list[str]:
        return list(cls._dumpers.keys())

    @classmethod
    def get(
        cls, kind_: Literal["load", "dump"], obj_key: str, /
    ) -> Loader | Dumper:
        try:
            match kind_:
                case "load":
                    return cls._loaders[obj_key]
                case "dump":
                    return cls._dumpers[obj_key]
            raise KeyError(
                f"No {kind_}er found for {obj_key}. "
                "Check if it is registered."
            )
        except Exception as e:
            raise e

    @classmethod
    def load(
        cls,
        subj_cls: type[Collective],
        obj: Any,
        obj_key: str = None,
        /,
        **kwargs,
    ) -> dict[str, Any]:
        return cls.get("load", obj_key).load_from(subj_cls, obj, **kwargs)

    @classmethod
    def dump(
        cls,
        subj: Collective,
        obj_key: str,
        /,
        **kwargs,
    ):
        return cls.get("dump", obj_key).dump_to(subj, **kwargs)


__all__ = ["AdapterRegistry", "Loader", "Dumper"]
