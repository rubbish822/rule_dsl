import datetime

from enum import Enum


class DSL(Enum):
    IF = 'if'
    THEN = 'then'
    ELSE_IF = 'elseif'
    ELSE = 'else'
    END = 'end'


class ParserEnum(Enum):
    """
    priority: or < and < in = not in
    """
    AND = ' and '
    IN = ' in '
    NOT_IN = ' not in '
    OR = ' or '


class ParamsPrefix(Enum):
    FUN = '@fun.'
    FAC = '@fac.'
    ACT = '@act.'


RTYPE_MAP = {
    'int': int,
    'float': float,
    'str': str,
    'list': list,
    'dict': dict,
    'bool': bool,
    'date': datetime.date,
    'datetime': datetime.datetime
}
