from typing import Literal

from lion_core.setting import LN_UNDEFINED
from lion_core.sys_utils import SysUtil
from lion_core.abc import BaseManager, BaseRecord
from lion_core.exceptions import LionValueError
from lion_core.task.base import BaseTask
from lion_core.task.dynamic_task import DynamicTask
from lion_core.task.static_task import StaticTask
from lion_core.task.appending_task import Task
from lion_core.generic.form import Form


# task manager fill task with info from record, kwargs or other tasks
class TaskManager(BaseManager):

    @staticmethod
    def create_task(
        *,
        assignment: str,
        subjective: BaseRecord | None = None,
        task_description=None,
        fill_inputs: bool = True,
        none_as_valid_value: bool = False,
        task_type: Literal["static", "dynamic", "appending"] = "appending",
        fill_which: Literal["input", "request", "both"] = "both",
        **kwargs,  # additional input value
    ):

        config = {
            "assignment": assignment,
            "task_description": task_description,
            "fill_inputs": fill_inputs,
            "none_as_valid_value": none_as_valid_value,
        }

        task = None

        if task_type == "static" and subjective is not None:
            task = StaticTask.from_record(subjective=subjective, **config)
            TaskManager.fill(task, fill_which=fill_which, **kwargs)

        else:
            if task_type == "dynamic":
                task = DynamicTask(**config)
            elif task_type == "appending":
                task = Task(**config)

            TaskManager.fill(task, subjective, fill_which=fill_which, **kwargs)

            return task

    @staticmethod
    def fill(
        obj_: BaseTask | Form,
        subj_: BaseTask | Form | None = None,
        /,
        fill_which: Literal["input", "request", "both"] = "both",
        **kwargs,
    ):
        if not isinstance(obj_, (BaseTask, Form)):
            raise LionValueError("Invalid objective to fill.")
        if subj_ and not isinstance(subj_, (BaseTask, Form)):
            raise LionValueError("Invalid subjective for filling.")

        if fill_which in {"input", "both"}:
            _fill_input(obj_, subj_, **kwargs)
        if fill_which in {"request", "both"}:
            _fill_request(obj_, subj_, **kwargs)


def _fill_input(
    obj_: BaseTask | Form, subj_: BaseTask | Form | None = None, /, **kwargs
):
    for i in obj_.request_fields:
        if obj_.none_as_valid_value:
            if getattr(obj_, i) is not LN_UNDEFINED:
                continue
            value = kwargs.get(i, LN_UNDEFINED)
            if value is LN_UNDEFINED:
                value = SysUtil.copy(getattr(subj_, i, LN_UNDEFINED))
            if value is not LN_UNDEFINED:
                setattr(obj_, i, value)
        else:
            if getattr(obj_, i) is None or getattr(obj_, i) is LN_UNDEFINED:
                value = kwargs.get(i)
                if value is LN_UNDEFINED or value is None:
                    value = SysUtil.copy(getattr(subj_, i, LN_UNDEFINED))
                if value is not LN_UNDEFINED and value is not None:
                    setattr(obj_, i, value)


def _fill_request(
    obj_: BaseTask | Form, subj_: BaseTask | Form | None = None, /, **kwargs
):
    for i in obj_.request_fields:
        if obj_.none_as_valid_value:
            if getattr(obj_, i) is not LN_UNDEFINED:
                continue
            value = kwargs.get(i, LN_UNDEFINED)
            if value is LN_UNDEFINED:
                value = SysUtil.copy(getattr(subj_, i, LN_UNDEFINED))
            if value is not LN_UNDEFINED:
                setattr(obj_, i, value)
        else:
            if getattr(obj_, i) is None or getattr(obj_, i) is LN_UNDEFINED:
                value = kwargs.get(i)
                if value is LN_UNDEFINED or value is None:
                    value = SysUtil.copy(getattr(subj_, i, LN_UNDEFINED))
                if value is not LN_UNDEFINED and value is not None:
                    setattr(obj_, i, value)
