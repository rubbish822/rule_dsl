class DSLError(Exception):
    pass


class ParserError(DSLError):
    pass


class GrammarError(DSLError):
    pass


class MatchError(DSLError):
    pass


class BracketsError(MatchError):
    pass


class RunnerError(DSLError):
    pass


class TypeParseError(DSLError):
    pass


class ACTError(DSLError):
    pass


def exception_handler(exc):
    raise exc
