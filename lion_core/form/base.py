"""
Base class for handling form-like structures within an application.

This module defines the BaseForm class, which manages form components and
operations such as filling forms and checking their state (filled, workable).

NOTICE:
    The Form/Report system takes inspiration from DSPy's approach to
    declarative language model calls, particularly its use of `Signature`
    and `Module`. However, this implementation is an original development
    by LionAGI.
    
    For reference to the inspiring work:
    https://github.com/stanfordnlp/dspy

    MIT License
    Copyright (c) 2023 Stanford Future Data Systems

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

REFERENCES:
    @article{khattab2023dspy,
    title={DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines},
    author={Khattab, Omar and Singhvi, Arnav and Maheshwari, Paridhi and Zhang, Zhiyuan and
    Santhanam, Keshav and Vardhamanan, Sri and Haq, Saiful and Sharma, Ashutosh and Joshi,
    Thomas T. and Moazam, Hanna and Miller, Heather and Zaharia, Matei and Potts, Christopher},
    journal={arXiv preprint arXiv:2310.03714},
    year={2023}
    }
    @article{khattab2022demonstrate,
    title={Demonstrate-Search-Predict: Composing Retrieval and Language Models for
    Knowledge-Intensive {NLP}},
    author={Khattab, Omar and Santhanam, Keshav and Li, Xiang Lisa and Hall, David and Liang,
    Percy and Potts, Christopher and Zaharia, Matei},
    journal={arXiv preprint arXiv:2212.14024},
    year={2022}
    }

LionAGI Implementation:
    This Form/Report system is an original development by LionAGI, created to address
    specific needs in form-based task handling. While inspired by concepts from DSPy,
    it has been independently designed and implemented with the following features:
    - Focused on form-based task handling
    - Fully integrated with LionAGI's existing collections and components
    - Includes a report system for multi-step task handling
    - Incorporates a work system for task execution and management
"""

from typing import Any, List, Dict
from abc import ABC
from pydantic import Field

from lion_core.generic.component import Component
from lion_core.setting import BASE_LION_FIELDS
from lion_core.sys_util import LN_UNDEFINED


class BaseForm(Component, ABC):
    """
    Base class for handling form-like structures within the Lion framework.

    This class defines the core structure and basic properties of a form,
    serving as a foundation for more specific form implementations.

    Attributes:
        template_name (str): The name of the form template.
        assignment (str): The objective of the form specifying input/output fields.
        input_fields (List[str]): Fields required to carry out the objective of the form.
        requested_fields (List[str]): Fields requested to be filled by the user.
        task (Any): The work to be done by the form, including custom instructions.
        validation_kwargs (Dict[str, Dict[str, Any]]): Additional validation constraints for the form fields.
    """

    template_name: str = "default_form"

    assignment: str = Field(
        ...,
        description="The objective of the form specifying input/output fields.",
        examples=["input1, input2 -> output"],
    )

    input_fields: List[str] = Field(
        default_factory=list,
        description="Fields required to carry out the objective of the form.",
    )

    requested_fields: List[str] = Field(
        default_factory=list,
        description="Fields requested to be filled by the user.",
    )

    task: Any = Field(
        default_factory=str,
        description="The work to be done by the form, including custom instructions.",
    )

    validation_kwargs: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional validation constraints for the form fields.",
        examples=[{"field": {"config1": "a", "config2": "b"}}],
    )

    @property
    def work_fields(self) -> Dict[str, Any]:
        """
        Get the fields relevant to the current task, including input and
        requested fields.

        Returns:
            Dict[str, Any]: The fields relevant to the current task.
        """
        dict_ = self.model_dump()
        return {
            k: v
            for k, v in dict_.items()
            if k not in BASE_LION_FIELDS
            and k in self.input_fields + self.requested_fields
        }

    @property
    def filled(self) -> bool:
        """
        Check if the form is filled with all required fields.

        Returns:
            bool: True if the form is filled, otherwise False.
        """
        return self._is_filled()

    def _is_filled(self) -> bool:
        """
        Check if all work fields are filled.

        Returns:
            bool: True if all work fields are filled, False otherwise.
        """
        return all(
            getattr(self, field, None) not in [None, LN_UNDEFINED]
            for field in self.work_fields
        )


# File: lion_core/form/base.py
