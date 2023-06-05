import functools
import logging
import re
import typing

from . import common, constants, enums, exceptions, text_parser
from .log import logger
from .matcher import TreeMatcher
from .parser import Parser, ConditionParser


class BaseEngine:
    type_ = None
    text_parser = text_parser.BaseText

    def __init__(
        self,
        grammar: str,
        text: str,
        user: typing.Optional[common.User] = None,
        parser: Parser = ConditionParser,
        tree_matcher: TreeMatcher = TreeMatcher,
        allow_no_params: bool = False,
        log: logging.Logger = logger,
    ):
        self.grammar = grammar
        self.text_str = text
        self.user = user
        self._text = self.text_parser
        self._parser = parser
        self._tree_matcher = tree_matcher
        self.end_msg = (None, '')
        self.allow_no_params = allow_no_params
        self.log = log
        self.chosed_runner = None

    @functools.cached_property
    def text(self):
        return self._text(self.text_str, self.user)

    @functools.cached_property
    def parser(self):
        return self._parser(self.grammar)

    @functools.cached_property
    def tree_matcher(self):
        return self._tree_matcher(self)

    @functools.cached_property
    def parsed_string_list(self):
        return self.parser.parsed_string_list

    def match_tree(self):
        raise NotImplementedError(
            'subclasses of BaseEngine must provide a match_tree() method'
        )


class BaseDSL(BaseEngine):
    def check_type(self) -> str:
        """check string type

        Returns:
            str: _description_
        """
        type_ = None
        line_string = self.text.value
        for item in enums.ParamsPrefix:
            if item.value in line_string:
                type_ = item.value.replace('@', '').replace('.', '')
        return type_

    @functools.lru_cache
    def run_fac(self, fac_name: str) -> bool:
        """
        Args:
            fac_name (str): @fac.is_admin_user

        """
        fac = getattr(self, fac_name.replace(enums.ParamsPrefix.FAC.value, ''))
        if not fac:
            raise exceptions.DSLError(f'no {fac_name} factor')
        self.chosed_runner = fac
        self.log.debug('[chosed_runner]: %s, [fac_name]: %s', fac, fac_name)
        return fac()

    @functools.lru_cache
    def run_fun(self, func_name: str, *args, **kwargs) -> any:
        """
        Args:
            func_name (str): 1. @fun.is_char_lower(@fac.sql_type)
                             2. @fun.is_char_lower("UPPER")
                             3. @func.func_name(4,5)

        """
        find_list = re.findall(constants.BRACKETS_REGEX, func_name)
        if not find_list:
            fun = getattr(self, func_name.replace(enums.ParamsPrefix.FUN.value, ''))
            if not fun:
                raise exceptions.DSLError(f'There is no {func_name} function')
            return fun(*args, **kwargs)
        else:
            args_string = find_list[0]
            args = []
            for arg in args_string.split(','):
                if enums.ParamsPrefix.FAC.value not in arg:
                    args.append(
                        arg.replace('"', '').replace("'", '')
                        if isinstance(arg, str) and ('"' in arg or "'" in arg)
                        else arg
                    )
                else:
                    args.append(self.run_fac(arg))
            fun = getattr(
                self,
                func_name.replace(enums.ParamsPrefix.FUN.value, '')
                .replace(args_string, '')
                .replace('()', ''),
            )
            if not fun:
                raise exceptions.DSLError(f'There is no {func_name} function')
            self.chosed_runner = fun
            self.log.debug('[chosed_runner]: %s, [func_name]: %s', fun, func_name)
            return fun(*args, **kwargs)

    @functools.lru_cache
    def run_act(self, act_name: str) -> bool:
        """
        Args:
            act_name (str): 1. @act.allow_execute
                            2. @act.reject_execute "只能执行查询语句"
        """
        act_str_list = act_name.strip().split(' ')
        args = []
        act = None
        for arg_str in act_str_list:
            if enums.ParamsPrefix.ACT.value in arg_str:
                act = getattr(
                    self, arg_str.strip().replace(enums.ParamsPrefix.ACT.value, '')
                )
            else:
                args.append(arg_str)
        if not act:
            raise exceptions.DSLError(f'no action {act_name}')
        self.chosed_runner = act
        self.log.debug('[chosed_runner]: %s, [act_name]: %s', act, act_name)
        return act(' '.join(args))

    @functools.lru_cache
    def chose_runner(self, line_string: str) -> any:
        self.chosed_runner = runner = None
        for params in enums.ParamsPrefix:
            if params.value in line_string:
                runner = getattr(self, f'run_{params.value.replace("@", "").replace(".", "")}')
        if not runner:
            self.log.debug(
                '[chose_runner]: [self.allow_no_params] is %s', self.allow_no_params
            )
            if not self.allow_no_params:
                raise exceptions.DSLError('Parameter error, parameter name not found')

        self.log.debug('[chose_runner]: %s, [line_string]: %s', runner, line_string)
        try:
            if callable(runner):
                result = runner(line_string)
            else:
                result = common.BoolValue(line_string).to_representation()
        except Exception as err:
            raise exceptions.ACTError() from err
        else:
            self.log.debug(
                '[chose_runner], %s, [line_string]: %s, [result]: %s',
                runner,
                line_string,
                result,
            )
            return result

    def match_tree(self):
        try:
            result = self.tree_matcher.match_tree()
        except Exception as err:
            exceptions.exception_handler(err)
        else:
            self.log.debug('[matched result]: %s', self.tree_matcher.matched)
        return result


class BaseCommonDSL(BaseDSL, common.CommonFAT):
    pass
