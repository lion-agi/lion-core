from enum import Enum
from lion_core.rule.default_rules.choice import ChoiceRule
from lion_core.rule.default_rules.mapping import MappingRule
from lion_core.rule.default_rules.number import NumberRule
from lion_core.rule.default_rules.boolean import BooleanRule
from lion_core.rule.default_rules.string import StringRule
from lion_core.rule.default_rules.action import ActionRequestRule


class DEFAULT_RULES(Enum):
    CHOICE = ChoiceRule
    MAPPING = MappingRule
    NUMBER = NumberRule
    BOOL = BooleanRule
    STR = StringRule
    ACTION = ActionRequestRule
