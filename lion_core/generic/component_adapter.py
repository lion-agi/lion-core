import json

from lionfuncs import to_dict

from lion_core.protocols.adapter import Adapter, AdapterRegistry


class JsonDataAdapter(Adapter):

    obj_key = "json_data"
    verbose = False
    config = {}

    @classmethod
    def from_obj(cls, subj_cls, obj, **kwargs):
        return to_dict(obj, **kwargs)

    @classmethod
    def to_obj(cls, subj, **kwargs):
        dict_ = subj.to_dict()
        return json.dumps(dict_, **kwargs)


class ComponentAdapterRegistry(AdapterRegistry):
    pass


ComponentAdapterRegistry.register(JsonDataAdapter)

__all__ = ["ComponentAdapterRegistry"]
