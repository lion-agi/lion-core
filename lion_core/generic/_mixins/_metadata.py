import lion_core.libs as libs
from lion_core.libs import SysUtils
from typing import TypeVar

T = TypeVar("T")


class ComponentMetaManageMixin:

    def _add_last_update(self, name):
        if (a := libs.nget(self.metadata, ["last_updated", name], None)) is None:
            libs.ninsert(
                self.metadata,
                ["last_updated", name],
                SysUtils.time(),
            )
        elif isinstance(a, tuple) and isinstance(a[0], int):
            libs.nset(
                self.metadata,
                ["last_updated", name],
                SysUtils.time(),
            )

    def _meta_pop(self, indices, default=...):
        indices = (
            indices
            if not isinstance(indices, list)
            else "|".join([str(i) for i in indices])
        )
        dict_ = self.metadata.copy()
        dict_ = libs.flatten(dict_)

        try:
            out_ = dict_.pop(indices, default) if default != ... else dict_.pop(indices)
        except KeyError as e:
            if default == ...:
                raise KeyError(f"Key {indices} not found in metadata.") from e
            return default

        a = libs.unflatten(dict_)
        self.metadata.clear()
        self.metadata.update(a)
        return out_

    def _meta_insert(self, indices, value):
        libs.ninsert(self.metadata, indices, value)

    def _meta_set(self, indices, value):
        if not self._meta_get(indices):
            self._meta_insert(indices, value)
        libs.nset(self.metadata, indices, value)

    def _meta_get(self, indices, default=...):
        if default != ...:
            return libs.nget(self.metadata, indices=indices, default=default)
        return libs.nget(self.metadata, indices)

    def __setattr__(self, name, value):
        if name == "metadata":
            raise AttributeError("Cannot directly assign to metadata.")
        super().__setattr__(name, value)
        self._add_last_update(name)
