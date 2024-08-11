"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import Literal, TYPE_CHECKING
from lion_core.libs import validate_mapping

from lion_core.session.branch import Branch
from lion_core.form.report import Report
from lion_core.generic.note import note
from lion_core.communication.action_request import ActionRequest
from lion_core.communication.action_response import ActionResponse
from lion_core.unit.process_action_request import process_action_request
from lion_core.unit.unit_form import UnitForm

if TYPE_CHECKING:
    from lion_core.session.branch import Branch


async def process_act(
    branch: Branch,
    form: UnitForm,
    report: Report,
    actions: dict,
    handle_unmatched: Literal["ignore", "raise", "remove", "force"] = "force",
    return_branch: bool = False,
) -> UnitForm | tuple[Branch, UnitForm]:
    """
    Process actions for a given branch and form.

    Args:
        branch: The branch to process actions for.
        form: The form associated with the actions.
        actions: A dictionary of actions to process.
        handle_unmatched: Strategy for handling unmatched actions.
        return_branch: Whether to return the branch along with the form.

    Returns:
        The updated form, or a tuple of (branch, form) if return_branch is True.

    Raises:
        ValueError: If no requests are found when processing actions.
    """
    if "action_performed" in form.all_fields and form.action_performed:
        if form.is_completed() and form not in report.completed_tasks:
            report.completed_tasks.include(form)
            report.completed_task_assignments[form.ln_id] = form.assignment
        return (branch, form) if return_branch else form

    action_keys = [f"action_{i+1}" for i in range(len(actions))]
    validated_actions = note(
        **validate_mapping(
            actions,
            action_keys,
            handle_unmatched=handle_unmatched,
        )
    )

    requests = []
    for k in action_keys:
        _func = validated_actions.get([k, "function"], "").replace("functions.", "")
        msg = ActionRequest(
            function=_func,
            arguments=validated_actions[k, "arguments"],
            sender=branch.ln_id,
            recipient=branch.tool_manager.registry[_func].ln_id,
        )
        requests.append(msg)
        branch.add_message(action_request=msg)

    if requests:
        out = await process_action_request(
            branch=branch, _msg=None, invoke_tool=True, action_request=requests
        )

        if out is False:
            raise ValueError("No requests found.")

        len_actions = len(validated_actions)
        action_responses = [
            i for i in branch.messages[-len_actions:] if isinstance(i, ActionResponse)
        ]

        _res = note()
        for idx, item in enumerate(action_responses):
            _res.insert(["action", idx], item.to_dict())

        len1 = len(form.action_response)

        if getattr(form, "action_response", None) is None:
            acts_ = _res.get(["action"], [])
            form.append_to_request("action_response", [i for i in acts_])
        else:
            form.action_response.extend([i for i in _res.get(["action"], [])])

        if len(form.action_response) > len1:
            form.append_to_request("action_performed", True)

    if form.is_completed() and form not in report.completed_tasks:
        report.completed_tasks.include(form)
        report.completed_task_assignments[form.ln_id] = form.assignment

    return (branch, form) if return_branch else form
