from typing import Any

from lion_core.libs import nmerge, validate_mapping
from lion_core.generic.form import Form
from lion_core.session.branch import Branch
from lion_core.unit.unit_form import create_unit_form
from lion_core.unit.process_chat import process_chat
from lion_core.unit.process_act import process_act


async def prepare_output(form: Form, verbose_direct: bool) -> Form:
    """
    Prepare the output form based on the action responses.

    Args:
        form: The form to prepare the output for.
        verbose: Whether to print verbose output.

    Returns:
        The prepared form with updated answer.
    """

    if "PLEASE_ACTION" in form.answer:
        if verbose_direct:
            print("Analyzing action responses and generating answer...")

        answer = await process_chat(
            "please provide final answer basing on the above"
            " information, provide answer value as a string only"
            " do not return as json, do not include other information",
        )

        if isinstance(answer, dict):
            a = answer.get("answer", None)
            if a is not None:
                answer = a

        answer = str(answer).strip()
        if answer.startswith("{") and answer.endswith("}"):
            answer = answer[1:-1]
            answer = answer.strip()
        if '"answer":' in answer:
            answer.replace('"answer":', "")
            answer = answer.strip()
        elif "'answer':" in answer:
            answer.replace("'answer':", "")
            answer = answer.strip()

        form.answer = answer

    return form


async def process_direct(
    branch: Branch,
    form: Form | None,
    instruction: str | None = None,
    context: dict[str, Any] | None = None,
    tools: Any | None = None,
    reason: bool = True,
    predict: bool = False,
    score: bool = True,
    select: Any | None = None,
    plan: Any | None = None,
    brainstorm: Any | None = None,
    reflect: Any | None = None,
    tool_schema: Any | None = None,
    allow_action: bool = False,
    allow_extension: bool = False,
    max_extension: int | None = None,
    confidence: Any | None = None,
    score_num_digits: int | None = None,
    score_range: tuple[float, float] | None = None,
    select_choices: list[str] | None = None,
    plan_num_step: int | None = None,
    predict_num_sentences: int | None = None,
    clear_messages: bool = False,
    verbose_direct: bool = True,
    image: str | list[str] | None = None,
    image_path: str | None = None,
    return_branch: bool = False,
    **kwargs: Any,
) -> tuple[Branch, Form] | Form:
    """
    Process a direct interaction with the model.

    Args:
        branch: The branch to process the interaction.
        form: The core form to be processed.
        instruction: The instruction for the interaction.
        context: The context for the interaction.
        tools: The tools to be used.
        reason: Whether to include reasoning.
        predict: Whether to include prediction.
        score: Whether to include scoring.
        select: Selection criteria.
        plan: Planning information.
        brainstorm: Brainstorming information.
        reflect: Reflection information.
        tool_schema: Schema for the tools.
        allow_action: Whether to allow actions.
        allow_extension: Whether to allow extensions.
        max_extension: Maximum number of extensions allowed.
        confidence: Confidence level.
        score_num_digits: Number of digits for scoring.
        score_range: Range for scoring.
        select_choices: Choices for selection.
        plan_num_step: Number of steps in the plan.
        predict_num_sentences: Number of sentences for prediction.
        clear_messages: Whether to clear messages.
        verbose: Whether to print verbose output.
        image: Image data for the interaction.
        image_path: Path to an image file.
        return_branch: Whether to return the branch along with the form.
        **kwargs: Additional keyword arguments for the chat process.

    Returns:
        The processed form, optionally with the branch.
    """
    branch, form = create_unit_form(
        branch=branch,
        form=form,
        instruction=instruction,
        context=context,
        tools=tools,
        reason=reason,
        predict=predict,
        score=score,
        select=select,
        plan=plan,
        brainstorm=brainstorm,
        reflect=reflect,
        tool_schema=tool_schema,
        allow_action=allow_action,
        allow_extension=allow_extension,
        max_extension=max_extension,
        confidence=confidence,
        score_num_digits=score_num_digits,
        score_range=score_range,
        select_choices=select_choices,
        plan_num_step=plan_num_step,
        predict_num_sentences=predict_num_sentences,
        clear_messages=clear_messages,
        return_branch=True,
    )

    if verbose_direct:
        print("Chatting with model...")

    form = await process_chat(
        branch=branch, form=form, image=image, image_path=image_path, **kwargs
    )

    if allow_action and getattr(form, "action_required", None):
        if actions := getattr(form, "actions", None):
            if verbose_direct:
                print(
                    "Found action requests in model response. " "Processing actions..."
                )

            form = await process_act(
                branch=branch,
                form=form,
                actions=actions,
                handle_unmatched="force",
                return_branch=True,
            )

            if verbose_direct:
                print("Actions processed!")

    last_form = form
    ctr = 0

    # Handle extensions if allowed and required
    extension_forms = []
    max_extension = max_extension if isinstance(max_extension, int) else 1
    plan_ = getattr(form, "plan", None)

    while (
        allow_extension
        and max_extension - ctr > 0
        and getattr(last_form, "extension_required", None)
    ):
        if verbose_direct:
            print(f"\nFound extension requests in model response.")
            print(f"------------------- Processing extension -------------------")

        # Ensure the next step in the plan is handled
        directive_kwargs = {
            "tools": tools,
            "reason": reason,
            "predict": predict,
            "score": score,
            "allow_action": allow_action,
            "confidence": confidence,
            "score_num_digits": score_num_digits,
            "score_range": score_range,
            "predict_num_sentences": predict_num_sentences,
            "max_extension": max_extension - ctr,
            **kwargs,
        }
        _ext = []
        if plan_:
            keys = [f"step_{i+1}" for i in range(len(plan_))]
            plan_ = validate_mapping(plan_, keys, handle_unmatched="force")

            for i in keys:
                directive_kwargs["instruction"] = plan[i]
                last_form = await process_direct(**directive_kwargs)
                directive_kwargs["max_extension"] -= 1

                last_form.add_field("is_extension", True)
                _ext.append(last_form)

                if directive_kwargs["max_extension"] <= 0:
                    break
                if not getattr(last_form, "extension_required", None):
                    break

        else:
            # Handle single step extension
            last_form = await process_direct(**directive_kwargs)
            last_form.add_field("is_extension", True)
            _ext.append(last_form)

        extension_forms.extend(_ext)
        last_form = _ext[-1] if isinstance(_ext, list) else _ext
        ctr += len(_ext)

    if extension_forms:

        if not getattr(form, "extension_forms", None):
            form.add_field("extension_forms", [])
        form.extension_forms.extend(extension_forms)

        action_responses = [
            i.action_response
            for i in extension_forms
            if getattr(i, "action_response", None) is not None
        ]

        if not hasattr(form, "action_response"):
            for action_response in action_responses:
                form.action_response.extend(action_response)

        for action_response in action_responses:
            nmerge([form.action_response, action_response])

    form = await prepare_output(form, verbose_direct)

    return form, branch if return_branch else form
