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

from enum import Enum
from typing import Any, TYPE_CHECKING

from pydantic import Field, PrivateAttr

from lion_core.libs import to_dict
from lion_core.form.base import BaseForm
from lion_core.form.report import Report

if TYPE_CHECKING:
    from lion_core.session.branch import Branch


class UnitForm(BaseForm):

    template_name: str = "UnitProcess"

    assignment: str = Field("task -> answer")

    confidence: float | None = Field(
        None,
        description=(
            "Provide a numeric confidence score on how likely you successfully "
            "achieved the task  between 0 and 1, with precision in 2 decimal "
            "places. 1 being very confident in a good job, 0 is not confident "
            "at all."
        ),
        validation_kwargs={
            "upper_bound": 1,
            "lower_bound": 0,
            "num_type": float,
            "precision": 2,
        },
    )

    reason: str | None = Field(  # Reason
        None,
        description=(
            "Explain yourself, provide concise reasoning for the process. "
            "Must start with: Let's think step by step, "
        ),
    )

    actions: dict | None = Field(  # Actions
        None,
        description=(
            "Actions to take based on the context and instruction. "
            "Format: {action_n: {function: ..., arguments: {param1: ..., "
            "param2: ...}}}. Leave blank if no actions are needed. "
            "Must use provided functions and parameters, DO NOT MAKE UP NAMES!!! "
            "Flag `action_required` as True if filled. When providing parameters, "
            "you must follow the provided type and format. If the parameter is a "
            "number, you should provide a number like 1/6, 23, 1.1, 314e-10, or 3.5-4j"
            "if float is allowed."
        ),
        examples=["{action_1: {function: 'add', arguments: {num1: 1, num2: 2}}}"],
    )

    action_required: bool | None = Field(
        None,
        description="Set to True if you provide actions, or provide actions if True.",
        examples=[True, False],
    )

    answer: str | None = Field(
        None,
        description=(
            "Adhere to the prompt and all user instructions. Provide the answer "
            "for the task. if actions are required at this step, set "
            "`action_required` to True and write only `PLEASE_ACTION` to the answer_field."
            "Additionally, if extensions are allowed and needed at this step to provide a"
            " high-quality, accurate answer, set extension_required to True and"
            "you will have another chance to provide the answer after the actions are done.",
        ),
    )

    extension_required: bool | None = Field(
        None,
        description=(
            "Set to True if more steps are needed to provide an accurate answer. "
            "If True, additional rounds are allowed."
        ),
        examples=[True, False],
    )

    prediction: str | None = Field(
        None,
        description="Provide the likely prediction based on context and instruction.",
    )

    plan: dict | str | None = Field(
        None,
        description=(
            "Provide a step-by-step plan. Format: {step_n: {plan: ..., reason: ...}}. "
            "Achieve the final answer at the last step. Set `extend_required` to True "
            "if plan requires more steps."
        ),
        examples=["{step_1: {plan: '...', reason: '...'}}"],
    )

    next_steps: dict | str | None = Field(
        None,
        description=(
            "Brainstorm ideas on next actions to take. Format: {next_step_n: {plan: "
            "..., reason: ...}}. Next_step is about anticipating future actions, "
            "but it does not have to be in a sequential format. Set `extend_required` "
            "to True if more steps are needed."
        ),
        examples=["{next_step_1: {plan: '...', reason: '...'}}"],
    )

    score: float | None = Field(
        None,
        description=(
            "A numeric score. Higher is better. If not otherwise instructed, "
            "fill this field with your own performance rating. Try hard and be "
            "self-critical."
        ),
        examples=[0.2, 5, 2.7],
    )

    reflection: str | None = Field(
        None,
        description=(
            "Reason your own reasoning. Create specific items on how/where/what "
            "you could improve to better achieve the task, or can the problem be "
            "solved in a different and better way. If you can think of a better "
            "solution, please provide it and fill the necessary fields in "
            "`action_required`, `extension_required`, `next_steps` if appropriate."
        ),
    )

    selection: Enum | str | list | None = Field(
        None, description="a single item from the choices."
    )

    tool_schema: list | dict | None = Field(
        None, description="The list of tools available for using."
    )

    # flag, should not be passed into LLM
    _action_performed: bool | None = PrivateAttr(None)
    _is_extension: bool = PrivateAttr(False)

    def __init__(
        self,
    ): ...

    def __init__(
        self,
        instruction=None,
        context=None,
        reason: bool = True,
        predict: bool = False,
        score=True,
        select=None,
        plan=None,
        brainstorm=None,
        reflect=None,
        tool_schema=None,
        allow_action: bool = False,
        allow_extension: bool = False,
        max_extension: int = None,
        confidence=None,
        score_num_digits=None,
        score_range=None,
        select_choices=None,
        plan_num_step=None,
        predict_num_sentences=None,
        **kwargs,
    ):

        super().__init__(**kwargs)

        self.task = (
            f"Follow the prompt and provide the necessary output.\n"
            f"- Additional instruction: {str(instruction or 'N/A')}\n"
            f"- Additional context: {str(context or 'N/A')}\n"
        )

        if reason:
            self.append_to_request("reason")

        if allow_action:
            self.append_to_request("actions")
            self.append_to_request("action_required")
            self.append_to_request("reason")
            self.task += "- Reason and prepare actions with GIVEN TOOLS ONLY.\n"

        if allow_extension:
            self.append_to_request("extension_required")
            self.task += (
                f"- Allow auto-extension up to another {max_extension} rounds.\n"
            )

        if tool_schema:
            self.append_to_input("tool_schema")
            self.tool_schema = tool_schema

        if brainstorm:
            self.append_to_request("next_steps")
            self.append_to_request("extension_required")
            self.task += "- Explore ideas on next actions to take.\n"

        if plan:
            plan_num_step = plan_num_step or 3
            max_extension = max_extension or plan_num_step
            allow_extension = True
            self.append_to_request("plan")
            self.append_to_request("extension_required")
            self.task += (
                f"- Generate a {plan_num_step}-step plan based on the context.\n"
            )

        if predict:
            self.append_to_request("prediction")
            self.task += (
                f"- Predict the next {predict_num_sentences or 1} sentence(s).\n"
            )

        if select:
            self.append_to_request("selection")
            self.task += (
                f"- Select 1 item from the provided choices: {select_choices}.\n"
            )

        if confidence:
            self.append_to_request("confidence_score")

        if score:
            self.append_to_request("score")

            score_range = score_range or [0, 10]
            score_num_digits = score_num_digits or 0

            self.validation_kwargs["score"] = {
                "upper_bound": score_range[1],
                "lower_bound": score_range[0],
                "num_type": int if score_num_digits == 0 else float,
                "precision": score_num_digits if score_num_digits != 0 else None,
            }

            self.task += (
                f"- Give a numeric score in [{score_range[0]}, {score_range[1]}] "
                f"and precision of {score_num_digits or 0} decimal places.\n"
            )

        if reflect:
            self.append_to_request("reflection")

    def display(self):
        """
        Display the current form fields and values in a user-friendly format.
        """
        fields = self.work_fields.copy()

        if "task" in fields and len(str(fields["task"])) > 2000:
            fields["task"] = fields["task"][:2000] + "..."

        if "tool_schema" in fields:
            tools = to_dict(fields["tool_schema"])["tools"]
            fields["available_tools"] = [i["function"]["name"] for i in tools]
            fields.pop("tool_schema")

        if "actions" in fields:
            a = ""
            idx = 0
            for _, v in fields["actions"].items():
                a += (
                    f"\n \n{idx+1}. **{v['function']}**"
                    f"({', '.join([f'{k}: {v}' for k, v in v['arguments'].items()])}), "
                )
                idx += 1
            fields["actions"] = a[:-2]

        if "action_response" in fields:
            a = ""
            idx = 0
            for _, v in fields["action_response"].items():
                a += (
                    f"\n \n{idx+1}. **{v['function']}**"
                    f"({', '.join([f'{k}: {v}' for k, v in v['arguments'].items()])})"
                )
                if len(str(v["output"])) > 30:
                    a += f" \n \n {v['output']}, "
                else:
                    a += f" = {v['output']}, "
                idx += 1
            fields["action_response"] = a[:-2]

        super().display(fields=fields)


def create_unit_form(
    branch: Branch,
    form: BaseForm | None,
    instruction: str | None = None,
    context: dict[str, Any] | None = None,
    tools: dict[str, Any] | None = None,
    reason: bool = True,
    predict: bool = False,
    score: bool = True,
    select: str | None = None,
    plan: dict[str, str] | None = None,
    brainstorm: str | None = None,
    reflect: str | None = None,
    tool_schema: dict[str, Any] | None = None,
    allow_action: bool = False,
    allow_extension: bool = False,
    max_extension: int | None = None,
    confidence: float | None = None,
    score_num_digits: int | None = None,
    score_range: tuple[float, float] | None = None,
    select_choices: list[str] | None = None,
    plan_num_step: int | None = None,
    predict_num_sentences: int | None = None,
    clear_messages: bool = False,
    return_branch: bool = False,
) -> tuple[Branch, UnitForm] | UnitForm:
    """
    Create a UnitForm instance based on the given parameters.

    Args:
        branch: The Branch instance to associate with the form.
        form: An existing Form instance to use as a base (optional).
        instruction: Additional instruction for the form.
        context: Additional context for the form.
        tools: Tools configuration for the form.
        reason: Flag to include reasoning in the form.
        predict: Flag to include prediction in the form.
        score: Flag to include scoring in the form.
        select: Selection parameter for the form.
        plan: Planning parameter for the form.
        brainstorm: Flag to include brainstorming in the form.
        reflect: Flag to include reflection in the form.
        tool_schema: Schema of available tools.
        allow_action: Flag to allow actions in the form.
        allow_extension: Flag to allow extensions in the form.
        max_extension: Maximum number of extensions allowed.
        confidence: Confidence parameter for the form.
        score_num_digits: Number of digits for scoring.
        score_range: Range for scoring.
        select_choices: Choices for selection.
        plan_num_step: Number of steps in the plan.
        predict_num_sentences: Number of sentences for prediction.
        clear_messages: Flag to clear existing messages.
        return_branch: Flag to return the branch along with the form.

    Returns:
        A tuple of (Branch, UnitForm) if return_branch is True, otherwise just
        the UnitForm.
    """
    if clear_messages:
        branch.clear()

    tool_schema = branch.tool_manager.get_tool_schema(tools) if tools else None
    if not form:
        form = UnitForm(
            instruction=instruction,
            context=context,
            reason=reason,
            predict=predict,
            score=score,
            select=select,
            plan=plan,
            tool_schema=tool_schema,
            allow_action=allow_action,
            allow_extension=allow_extension,
            max_extension=(
                1 if (allow_extension and max_extension is None) else max_extension
            ),
            confidence=confidence,
            score_num_digits=score_num_digits,
            score_range=score_range,
            select_choices=select_choices,
            plan_num_step=plan_num_step,
            predict_num_sentences=predict_num_sentences,
            brainstorm=brainstorm,
            reflect=reflect,
            tool_schema=tool_schema,
        )

    elif form and "tool_schema" not in form.all_fields:
        form.append_to_input("tool_schema", tool_schema)
    else:
        form.tool_schema = tool_schema

    return branch, form if return_branch else form
