import pytest
from lion_core.communication.action_request import ActionRequest
from lion_core.communication.action_response import (
    ActionResponse,
    prepare_action_response_content,
)
from lion_core.communication.message import MessageRole, MessageFlag
from lion_core.exceptions import LionValueError
from lion_core.generic.note import Note


# Tests for prepare_action_response_content function
def test_prepare_action_response_content():
    request = ActionRequest("test_func", {"arg1": 1}, "sender1", "recipient1")
    content = prepare_action_response_content(request, "result")
    assert isinstance(content, Note)
    assert content.get("action_request_id") == request.ln_id
    assert content.get(["action_response", "function"]) == "test_func"
    assert content.get(["action_response", "arguments"]) == {"arg1": 1}
    assert content.get(["action_response", "output"]) == "result"


def test_prepare_action_response_content_already_responded():
    request = ActionRequest("test_func", {}, "sender1", "recipient1")
    request.content["action_response_id"] = "existing_response"
    with pytest.raises(LionValueError):
        prepare_action_response_content(request, "result")


# Tests for ActionResponse class
def test_action_response_init():
    request = ActionRequest("test_func", {"arg1": 1}, "sender1", "recipient1")
    response = ActionResponse(request, "sender2", "result")
    assert response.role == MessageRole.ASSISTANT
    assert response.sender == "sender2"
    assert response.recipient == "sender1"
    assert response.func_output == "result"
    assert request.is_responded


def test_action_response_init_with_message_load():
    protected_params = {
        "role": MessageRole.ASSISTANT,
        "content": Note(),
        "sender": "sender2",
    }
    response = ActionResponse(
        MessageFlag.MESSAGE_LOAD,
        MessageFlag.MESSAGE_LOAD,
        MessageFlag.MESSAGE_LOAD,
        protected_init_params=protected_params,
    )
    assert response.role == MessageRole.ASSISTANT
    assert response.sender == "sender2"


def test_action_response_init_with_message_clone():
    response = ActionResponse(
        MessageFlag.MESSAGE_CLONE, MessageFlag.MESSAGE_CLONE, MessageFlag.MESSAGE_CLONE
    )
    assert response.role == MessageRole.ASSISTANT


def test_action_response_func_output():
    request = ActionRequest("test_func", {}, "sender1", "recipient1")
    response = ActionResponse(request, "sender2", "result")
    assert response.func_output == "result"


def test_action_response_response_dict():
    request = ActionRequest("test_func", {"arg1": 1}, "sender1", "recipient1")
    response = ActionResponse(request, "sender2", "result")
    assert response.response_dict == {
        "function": "test_func",
        "arguments": {"arg1": 1},
        "output": "result",
    }


def test_action_response_action_request_id():
    request = ActionRequest("test_func", {}, "sender1", "recipient1")
    response = ActionResponse(request, "sender2", "result")
    assert response.action_request_id == request.ln_id


def test_action_response_update_request():
    request1 = ActionRequest("func1", {"arg1": 1}, "sender1", "recipient1")
    response = ActionResponse(request1, "sender2", "result1")

    request2 = ActionRequest("func2", {"arg2": 2}, "sender3", "recipient3")
    response.update_request(request2, "result2")

    assert response.func_output == "result2"
    assert response.response_dict["function"] == "func2"
    assert response.response_dict["arguments"] == {"arg2": 2}
    assert request2.is_responded


# Edge cases and additional tests for ActionResponse
def test_action_response_with_none_output():
    request = ActionRequest("test_func", {}, "sender1", "recipient1")
    response = ActionResponse(request, "sender2", None)
    assert response.func_output is None


def test_action_response_with_large_output():
    request = ActionRequest("test_func", {}, "sender1", "recipient1")
    large_output = "a" * 1000000  # 1MB string
    response = ActionResponse(request, "sender2", large_output)
    assert len(response.func_output) == 1000000


def test_action_response_unicode():
    request = ActionRequest("test_func", {"arg": "你好世界"}, "sender1", "recipient1")
    response = ActionResponse(request, "sender2", "こんにちは世界")
    assert response.func_output == "こんにちは世界"


def test_action_response_update_with_different_argument_structure():
    request1 = ActionRequest("func1", {"arg1": 1}, "sender1", "recipient1")
    response = ActionResponse(request1, "sender2", "result1")

    request2 = ActionRequest("func2", {"arg2": [1, 2, 3]}, "sender3", "recipient3")
    response.update_request(request2, {"complex": "output"})

    assert response.response_dict["arguments"] == {"arg2": [1, 2, 3]}
    assert response.func_output == {"complex": "output"}


def test_action_response_multiple_updates():
    request = ActionRequest("func1", {"arg1": 1}, "sender1", "recipient1")
    response = ActionResponse(request, "sender2", "result1")

    for i in range(10):
        new_request = ActionRequest(
            f"func{i+2}", {f"arg{i+2}": i + 2}, f"sender{i+3}", f"recipient{i+3}"
        )
        response.update_request(new_request, f"result{i+2}")

    assert response.func_output == "result11"
    assert response.response_dict["function"] == "func11"
    assert response.response_dict["arguments"] == {"arg11": 11}


def test_action_response_serialization():
    import json

    request = ActionRequest(
        "test_func", {"arg1": 1, "arg2": [1, 2, 3]}, "sender1", "recipient1"
    )
    response = ActionResponse(
        request, "sender2", {"result": "complex", "data": [4, 5, 6]}
    )

    # Serialize
    response_json = json.dumps(response.to_dict())

    # Deserialize
    reconstructed_response = ActionResponse.from_dict(json.loads(response_json))

    assert reconstructed_response.response_dict == response.response_dict


def test_action_response_with_very_deep_nesting():
    def create_nested_dict(depth):
        if depth == 0:
            return {"value": "bottom"}
        return {"nested": create_nested_dict(depth - 1)}

    deep_args = create_nested_dict(100)  # Very deep nesting
    request = ActionRequest("deep_func", deep_args, "sender1", "recipient1")
    response = ActionResponse(request, "sender2", create_nested_dict(100))

    assert response.func_output == deep_args


def test_action_response_thread_safety():
    import threading

    def create_response():
        request = ActionRequest(
            "thread_func", {"thread_id": threading.get_ident()}, "sender", "recipient"
        )
        ActionResponse(
            request, "responder", f"Response from thread {threading.get_ident()}"
        )

    threads = [threading.Thread(target=create_response) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # No assertion needed; if this runs without errors, it's thread-safe


def test_action_response_performance():
    import time

    start_time = time.time()
    request = ActionRequest("perf_func", {"arg": 0}, "sender", "recipient")
    for _ in range(10000):
        ActionResponse(request, "responder", f"Result {_}")
    end_time = time.time()

    assert end_time - start_time < 5  # Should complete in less than 5 seconds


def test_action_response_with_invalid_utf8():
    request = ActionRequest("test_func", {}, "sender1", "recipient1")
    invalid_utf8 = b"Invalid UTF-8: \xff"
    with pytest.raises(UnicodeDecodeError):
        ActionResponse(request, "sender2", invalid_utf8.decode("utf-8"))


def test_action_response_with_various_output_types():
    request = ActionRequest("test_func", {}, "sender1", "recipient1")
    outputs = [42, 3.14, True, "string", [1, 2, 3], {"key": "value"}, None, b"bytes"]
    for output in outputs:
        response = ActionResponse(request, "sender2", output)
        assert response.func_output == output


def test_action_response_with_no_sender():
    request = ActionRequest("test_func", {}, "sender1", "recipient1")
    response = ActionResponse(request, None, "result")
    assert response.sender == "N/A"


def test_action_response_update_with_same_request():
    request = ActionRequest("func1", {"arg1": 1}, "sender1", "recipient1")
    response = ActionResponse(request, "sender2", "result1")

    response.update_request(request, "new_result")

    assert response.func_output == "new_result"
    assert response.response_dict["function"] == "func1"
    assert response.response_dict["arguments"] == {"arg1": 1}


def test_action_response_with_very_long_function_name():
    long_name = "a" * 1000
    request = ActionRequest(long_name, {}, "sender1", "recipient1")
    response = ActionResponse(request, "sender2", "result")
    assert len(response.response_dict["function"]) == 1000


def test_action_response_with_maximum_arguments():
    max_args = {f"arg{i}": i for i in range(1000)}  # 1000 arguments
    request = ActionRequest("max_args_func", max_args, "sender1", "recipient1")
    response = ActionResponse(request, "sender2", "result")
    assert len(response.response_dict["arguments"]) == 1000


def test_action_response_with_circular_reference_in_output():
    class CircularRef:
        def __init__(self):
            self.ref = self

    request = ActionRequest("test_func", {}, "sender1", "recipient1")
    circular = CircularRef()

    with pytest.raises(Exception):  # Expect some kind of serialization error
        ActionResponse(request, "sender2", circular)


def test_action_response_update_request_idempotency():
    request1 = ActionRequest("func1", {"arg1": 1}, "sender1", "recipient1")
    response = ActionResponse(request1, "sender2", "result1")

    request2 = ActionRequest("func2", {"arg2": 2}, "sender3", "recipient3")
    response.update_request(request2, "result2")
    response.update_request(request2, "result2")  # Update with the same request again

    assert response.func_output == "result2"
    assert response.response_dict["function"] == "func2"
    assert response.response_dict["arguments"] == {"arg2": 2}
    assert request2.is_responded


def test_action_response_with_empty_request():
    request = ActionRequest("empty_func", {}, "", "")
    response = ActionResponse(request, "", "")
    assert response.sender == "N/A"
    assert response.recipient == ""
    assert response.func_output == ""


def test_action_response_with_very_large_request_and_response():
    large_args = {"arg": "a" * 1000000}  # 1MB of arguments
    request = ActionRequest("large_func", large_args, "sender1", "recipient1")
    large_output = "b" * 1000000  # 1MB of output
    response = ActionResponse(request, "sender2", large_output)

    assert len(response.response_dict["arguments"]["arg"]) == 1000000
    assert len(response.func_output) == 1000000


# Test to ensure that updating a response doesn't affect the original request
def test_action_response_update_request_isolation():
    request1 = ActionRequest("func1", {"arg1": 1}, "sender1", "recipient1")
    response = ActionResponse(request1, "sender2", "result1")

    request2 = ActionRequest("func2", {"arg2": 2}, "sender3", "recipient3")
    response.update_request(request2, "result2")

    assert request1.request_dict["function"] == "func1"
    assert request1.request_dict["arguments"] == {"arg1": 1}
    assert not request1.is_responded


# Test to ensure proper handling of updates with different types
def test_action_response_update_with_different_types():
    request1 = ActionRequest("func1", {"arg1": 1}, "sender1", "recipient1")
    response = ActionResponse(request1, "sender2", "result1")

    request2 = ActionRequest("func2", {"arg2": "string"}, "sender3", "recipient3")
    response.update_request(request2, 42)

    assert response.func_output == 42
    assert response.response_dict["arguments"] == {"arg2": "string"}


# Test to ensure that the action_request_id is properly updated
def test_action_response_update_action_request_id():
    request1 = ActionRequest("func1", {}, "sender1", "recipient1")
    response = ActionResponse(request1, "sender2", "result1")

    request2 = ActionRequest("func2", {}, "sender3", "recipient3")
    response.update_request(request2, "result2")

    assert response.action_request_id == request2.ln_id


# Test for potential memory leaks
def test_action_response_memory_usage():
    import sys

    request = ActionRequest("mem_func", {}, "sender1", "recipient1")
    initial_memory = sys.getsizeof(request) + sys.getsizeof(
        ActionResponse(request, "sender2", "result")
    )

    for _ in range(1000):
        response = ActionResponse(request, "sender2", "result")
        response.update_request(request, "new_result")

    final_memory = sys.getsizeof(request) + sys.getsizeof(response)

    # Ensure memory usage hasn't increased significantly
    assert final_memory < initial_memory * 1.1  # Allow for some small increase
