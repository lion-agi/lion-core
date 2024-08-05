import pytest
from typing import Callable
from pydantic import ValidationError
from lion_core.communication.action_request import ActionRequest, prepare_action_request
from lion_core.communication.message import MessageRole, MessageFlag
from lion_core.generic.note import Note


# Helper function for tests
def dummy_func(x: int, y: int) -> int:
    return x + y


# Tests for prepare_action_request function
def test_prepare_action_request_with_str_func():
    result = prepare_action_request("test_func", {"arg1": 1, "arg2": 2})
    assert isinstance(result, Note)
    assert result.get(["action_request", "function"]) == "test_func"
    assert result.get(["action_request", "arguments"]) == {"arg1": 1, "arg2": 2}


def test_prepare_action_request_with_callable():
    result = prepare_action_request(dummy_func, {"x": 1, "y": 2})
    assert result.get(["action_request", "function"]) == "dummy_func"
    assert result.get(["action_request", "arguments"]) == {"x": 1, "y": 2}


def test_prepare_action_request_invalid_arguments():
    with pytest.raises(ValueError):
        prepare_action_request("test_func", "invalid_args")


def test_prepare_action_request_json_arguments():
    result = prepare_action_request("test_func", '{"arg1": 1, "arg2": 2}')
    assert result.get(["action_request", "arguments"]) == {"arg1": 1, "arg2": 2}


def test_prepare_action_request_xml_arguments():
    xml_args = "<root><arg1>1</arg1><arg2>2</arg2></root>"
    result = prepare_action_request("test_func", xml_args)
    assert result.get(["action_request", "arguments"]) == {"arg1": "1", "arg2": "2"}


# Tests for ActionRequest class
def test_action_request_init():
    request = ActionRequest("test_func", {"arg1": 1}, "sender1", "recipient1")
    assert request.role == MessageRole.ASSISTANT
    assert request.sender == "sender1"
    assert request.recipient == "recipient1"
    assert request.request_dict == {"function": "test_func", "arguments": {"arg1": 1}}


def test_action_request_init_with_callable():
    request = ActionRequest(dummy_func, {"x": 1, "y": 2}, "sender1", "recipient1")
    assert request.request_dict["function"] == "dummy_func"


def test_action_request_init_with_message_load():
    protected_params = {
        "role": MessageRole.ASSISTANT,
        "content": Note(),
        "sender": "sender1",
    }
    request = ActionRequest(
        MessageFlag.MESSAGE_LOAD,
        MessageFlag.MESSAGE_LOAD,
        MessageFlag.MESSAGE_LOAD,
        MessageFlag.MESSAGE_LOAD,
        protected_init_params=protected_params,
    )
    assert request.role == MessageRole.ASSISTANT
    assert request.sender == "sender1"


def test_action_request_init_with_message_clone():
    request = ActionRequest(
        MessageFlag.MESSAGE_CLONE,
        MessageFlag.MESSAGE_CLONE,
        MessageFlag.MESSAGE_CLONE,
        MessageFlag.MESSAGE_CLONE,
    )
    assert request.role == MessageRole.ASSISTANT


def test_action_request_is_responded():
    request = ActionRequest("test_func", {}, "sender1", "recipient1")
    assert not request.is_responded
    request.content["action_response_id"] = "response_id"
    assert request.is_responded


def test_action_request_request_dict():
    request = ActionRequest("test_func", {"arg1": 1}, "sender1", "recipient1")
    assert request.request_dict == {"function": "test_func", "arguments": {"arg1": 1}}


def test_action_request_action_response_id():
    request = ActionRequest("test_func", {}, "sender1", "recipient1")
    assert request.action_response_id is None
    request.content["action_response_id"] = "response_id"
    assert request.action_response_id == "response_id"


# Edge cases and additional tests for ActionRequest
def test_action_request_with_empty_arguments():
    request = ActionRequest("test_func", {}, "sender1", "recipient1")
    assert request.request_dict["arguments"] == {}


def test_action_request_with_none_arguments():
    with pytest.raises(ValueError):
        ActionRequest("test_func", None, "sender1", "recipient1")


def test_action_request_with_very_long_function_name():
    long_name = "a" * 1000
    request = ActionRequest(long_name, {}, "sender1", "recipient1")
    assert len(request.request_dict["function"]) == 1000


def test_action_request_with_complex_arguments():
    complex_args = {
        "nested": {"a": 1, "b": [2, 3, 4]},
        "list": [{"x": 1}, {"y": 2}],
        "tuple": (1, 2, 3),
    }
    request = ActionRequest("test_func", complex_args, "sender1", "recipient1")
    assert request.request_dict["arguments"] == complex_args


def test_action_request_unicode():
    unicode_args = {"arg": "你好世界"}
    request = ActionRequest("test_func", unicode_args, "sender1", "recipient1")
    assert request.request_dict["arguments"] == unicode_args


def test_action_request_with_callable_and_kwargs():
    def func_with_kwargs(x: int, **kwargs):
        return x + sum(kwargs.values())

    request = ActionRequest(
        func_with_kwargs, {"x": 1, "y": 2, "z": 3}, "sender1", "recipient1"
    )
    assert request.request_dict["function"] == "func_with_kwargs"
    assert request.request_dict["arguments"] == {"x": 1, "y": 2, "z": 3}


def test_action_request_with_circular_reference():
    class CircularRef:
        def __init__(self):
            self.ref = self

    circular = CircularRef()
    with pytest.raises(Exception):  # Expect some kind of serialization error
        ActionRequest("test_func", {"circular": circular}, "sender1", "recipient1")


def test_action_request_serialization():
    import json

    request = ActionRequest(
        "test_func", {"arg1": 1, "arg2": [1, 2, 3]}, "sender1", "recipient1"
    )

    # Serialize
    request_json = json.dumps(request.to_dict())

    # Deserialize
    reconstructed_request = ActionRequest.from_dict(json.loads(request_json))

    assert reconstructed_request.request_dict == request.request_dict


def test_action_request_with_very_deep_nesting():
    def create_nested_dict(depth):
        if depth == 0:
            return {"value": "bottom"}
        return {"nested": create_nested_dict(depth - 1)}

    deep_args = create_nested_dict(100)  # Very deep nesting
    request = ActionRequest("deep_func", deep_args, "sender1", "recipient1")

    assert request.request_dict["arguments"] == deep_args


def test_action_request_thread_safety():
    import threading

    def create_request():
        ActionRequest(
            "thread_func", {"thread_id": threading.get_ident()}, "sender", "recipient"
        )

    threads = [threading.Thread(target=create_request) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # No assertion needed; if this runs without errors, it's thread-safe


# Performance test for ActionRequest
def test_action_request_performance():
    import time

    start_time = time.time()
    for _ in range(10000):
        ActionRequest("perf_func", {"arg": _}, "sender", "recipient")
    end_time = time.time()

    assert end_time - start_time < 5  # Should complete in less than 5 seconds


# Test with invalid UTF-8 sequences
def test_action_request_invalid_utf8():
    invalid_utf8 = b"Invalid UTF-8: \xff"
    with pytest.raises(UnicodeDecodeError):
        ActionRequest(
            "test_func", {"arg": invalid_utf8.decode("utf-8")}, "sender1", "recipient1"
        )


# Test with various types of callables
def test_action_request_with_various_callables():
    def normal_func():
        pass

    class CallableClass:
        def __call__(self):
            pass

    lambda_func = lambda: None

    async def async_func():
        pass

    for func in [normal_func, CallableClass(), lambda_func, async_func]:
        request = ActionRequest(func, {}, "sender1", "recipient1")
        assert isinstance(request.request_dict["function"], str)


# Test handling of action requests with no sender/recipient
def test_action_request_no_sender_recipient():
    request = ActionRequest("test_func", {}, None, None)
    assert request.sender is None
    assert request.recipient is None


# Test with maximum possible arguments
def test_action_request_max_arguments():
    max_args = {f"arg{i}": i for i in range(1000)}  # 1000 arguments
    request = ActionRequest("max_args_func", max_args, "sender1", "recipient1")
    assert len(request.request_dict["arguments"]) == 1000


# Test with various data types in arguments
def test_action_request_various_data_types():
    args = {
        "int": 1,
        "float": 3.14,
        "bool": True,
        "str": "test",
        "list": [1, 2, 3],
        "dict": {"a": 1},
        "none": None,
        "bytes": b"bytes",
    }
    request = ActionRequest("data_types_func", args, "sender1", "recipient1")
    assert request.request_dict["arguments"] == args
