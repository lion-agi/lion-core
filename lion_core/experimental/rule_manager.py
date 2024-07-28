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

from lion_core.abc import BaseManager


from typing import Any, Dict, List, Union
from lion_core.sys_util import SysUtil
from lion_core.rule.base import Rule
from lion_core.rule.default_rules import DEFAULT_RULES
from lion_core.experimental.rulebook import RuleBook
from lion_core.record.form import Form
from lion_core.record.report import Report

_DEFAULT_RULEORDER = [
    "choice",
    "actionrequest",
    "number",
    "mapping",
    "str",
    "bool",
]

_DEFAULT_RULES = {
    "choice": DEFAULT_RULES.CHOICE.value,
    "actionrequest": DEFAULT_RULES.ACTION.value,
    "bool": DEFAULT_RULES.BOOL.value,
    "number": DEFAULT_RULES.NUMBER.value,
    "mapping": DEFAULT_RULES.MAPPING.value,
    "str": DEFAULT_RULES.STR.value,
}


class RuleManager(BaseManager):
    """
    Validator class to manage the validation of forms using a RuleBook.
    """

    def add_rule(self, rule_name: str, rule: Rule, config: dict = None):
        """
        Add a new rule to the validator.

        Args:
            rule_name (str): The name of the rule.
            rule (Rule): The rule object.
            config (dict, optional): Configuration for the rule.
        """
        if rule_name in self.active_rules:
            raise ValueError(f"Rule '{rule_name}' already exists.")
        self.active_rules[rule_name] = rule
        self.rulebook.rules[rule_name] = rule
        self.rulebook.ruleorder.append(rule_name)
        self.rulebook.rule_config[rule_name] = config or {}

    def remove_rule(self, rule_name: str):
        """
        Remove an existing rule from the validator.

        Args:
            rule_name (str): The name of the rule to remove.
        """
        if rule_name not in self.active_rules:
            raise ValueError(f"Rule '{rule_name}' does not exist.")
        del self.active_rules[rule_name]
        del self.rulebook.rules[rule_name]
        self.rulebook.ruleorder.remove(rule_name)
        del self.rulebook.rule_config[rule_name]

    def list_active_rules(self) -> list:
        """
        List all active rules.

        Returns:
            list: A list of active rule names.
        """
        return list(self.active_rules.keys())

    def enable_rule(self, rule_name: str, enable: bool = True):
        """
        Enable a specific rule.

        Args:
            rule_name (str): The name of the rule.
            enable (bool): Whether to enable or disable the rule.
        """
        if rule_name not in self.active_rules:
            raise ValueError(f"Rule '{rule_name}' does not exist.")
        self.active_rules[rule_name].enabled = enable

    def disable_rule(self, rule_name: str):
        """
        Disable a specific rule.

        Args:
            rule_name (str): The name of the rule to disable.
        """
        self.enable_rule(rule_name, enable=False)

    def log_validation_attempt(self, form: Form, result: dict):
        """
        Log a validation attempt.

        Args:
            form (Form): The form being validated.
            result (dict): The result of the validation.
        """
        log_entry = {
            "form_id": form.ln_id,
            "timestamp": SysUtil.get_timestamp(),
            "result": result,
        }
        self.validation_log.append(log_entry)

    def log_validation_error(self, field: str, value: Any, error: str):
        """
        Log a validation error.

        Args:
            field (str): The field that failed validation.
            value (Any): The value of the field.
            error (str): The error message.
        """
        log_entry = {
            "field": field,
            "value": value,
            "error": error,
            "timestamp": SysUtil.get_timestamp(),
        }
        self.validation_log.append(log_entry)

    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of validation results.

        Returns:
            dict: A summary of validation attempts, errors, and successful attempts.
        """
        summary = {
            "total_attempts": len(self.validation_log),
            "errors": [log for log in self.validation_log if "error" in log],
            "successful_attempts": [
                log for log in self.validation_log if "result" in log
            ],
        }
        return summary
