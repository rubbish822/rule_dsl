import operator
import re

OPERATOR_MAP = {
    '==': operator.eq,
    '!=': operator.ne,
    '>': operator.gt,
    '>=': operator.ge,
    '<': operator.lt,
    '<=': operator.le,
    'matchs': lambda a, regex: re.match(re.compile(regex), a),
    'not matchs': lambda a, regex: not re.match(re.compile(regex), a),
}

OPERATOR_REGEX = re.compile(r'==|!=|>=|>|<=|<|not matchs|matchs')
MATCH_REGEX = re.compile(r'@fun\.|@fac\.|@act\.')
BRACKETS_REGEX = re.compile(r'[(](.*)[)]', re.S)
BRACKETS_EMPTY_REGEX = re.compile(
    r'==|!=|>=|>|<=|<|and |in |not in |or |not matchs |matchs ', re.S
)
