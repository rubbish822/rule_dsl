import typing
from dataclasses import dataclass

from .utils import act

__all__ = ('User', 'BoolValue', 'CommonFAT')


@dataclass
class User:
    pk: str


class BoolValue:
    TRUE_VALUES = {'true', 'True', 'TRUE', True}
    FALSE_VALUES = {'false', 'False', 'FALSE', False}
    NULL_VALUES = {'null', 'Null', 'NULL', '', None}

    def __init__(self, value):
        self.value = value

    def to_representation(self) -> typing.Union[bool, typing.Any]:
        value = self.value
        if value in self.TRUE_VALUES:
            return True
        elif value in self.FALSE_VALUES:
            return False
        return value


class CommonFAT:
    @act
    def reject_execute(self, msg: str = None) -> bool:
        self.end_msg = (False, msg)
        self.log.debug(
            '[grammar]: %s, [text]: %s, [reject_execute]: %s',
            self.grammar,
            self.text.value,
            self.end_msg,
        )
        return False

    @act
    def allow_execute(self, msg: str = None) -> bool:
        self.end_msg = (True, msg)
        self.log.debug(
            '[grammar]: %s, [text]: %s, [allow_execute]: %s',
            self.grammar,
            self.text.value,
            self.end_msg,
        )
        return True
