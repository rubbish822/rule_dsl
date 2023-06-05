import json
import logging
import re
import typing

from . import common, constants, enums, exceptions
from .log import dsl_parser_log


class TreeMatcher:
    def __init__(self, dsl):
        self.dsl = dsl
        self.matched = None
        self.log: logging.Logger = dsl_parser_log
        self.match_cached = {'()': False}

    def match_in_or_not(self, notin_string_list: list, type_: str = 'in') -> bool:
        condition_str, value_str = (
            notin_string_list[0].strip(),
            notin_string_list[-1].strip(),
        )
        _, condition_value = self.get_condition_value(condition_str)
        if isinstance(condition_value, str) and (
            '"' in condition_value or "'" in condition_value
        ):
            try:
                condition_value = json.loads(condition_value)
            except json.decoder.JSONDecodeError:
                condition_value = condition_value.replace('"', '').replace("'", '')

        _, in_value = self.get_condition_value(value_str)

        if isinstance(in_value, str) and ('"' in in_value or "'" in in_value):
            try:
                in_value = json.loads(in_value)
            except json.decoder.JSONDecodeError:
                in_value = in_value.replace('"', '').replace("'", '')

        return (
            condition_value in in_value
            if type_ == 'in'
            else condition_value not in in_value
        )

    def match_condition(self, condition_str: str) -> bool:
        """match condition expression

        Args:
            condition_str (str): @fac.fac_value > 1 and @fun.is_char_lower("A") or @fac.char_length > 10

        Returns:
            bool: _description_
        """
        self.log.debug('[match_condition]: [condition_str]: %s', condition_str)
        _condition_str = condition_str.strip()
        if enums.ParserEnum.OR.value in _condition_str:
            _contidion_list = _condition_str.split(enums.ParserEnum.OR.value)
        else:
            _contidion_list = [_condition_str]
        or_result = False
        for _c_str in _contidion_list:
            or_result = self.match_or(_c_str)
            if or_result:
                or_result = True
                break
        return or_result

    def parse_rtype_value(self, value: typing.Any) -> typing.Any:
        """
        Convert data to a defined return data type
        """
        chosed_runner = self.dsl.chosed_runner
        if chosed_runner:
            rtype_value = chosed_runner.__dict__.get('_dict', {}).get('rtype')
            if rtype_value:
                rtype = enums.RTYPE_MAP[rtype_value]
                if isinstance(value, str):
                    if rtype in (int, float, str):
                        value = rtype(value)
                    elif rtype in (list, dict):
                        value = json.loads(value)
        return value

    def get_condition_value(self, condition_str: str) -> typing.Tuple[bool, typing.Any]:
        """Get the result of a conditional expression

        Args:
            condition_str (str): 1. @fac.fac_value in ["a"]
                                 2. @fac.fac_value in @fac.fac_list
                                 3. 1 in @fac.fac_value

        Raises:
            exceptions.RunnerError: runner error

        Returns:
            tuple: (is_fat, condition_value)
        """
        is_fat = False
        try:
            # '["a","b"]' json.loads正常, "['a','b']"不正常，需要前端输入标准json数据格式
            if re.search(constants.MATCH_REGEX, condition_str):
                # @fac.fac_value in ["a"]
                condition_value = self.dsl.chose_runner(condition_str)
                is_fat = True
            else:
                # "a" in @fac.fac_value
                condition_value = common.BoolValue(condition_str).to_representation()
        except Exception as err:
            raise exceptions.RunnerError(err)
        if isinstance(condition_value, str) and (
            '"' in condition_value or "'" in condition_value
        ):
            try:
                condition_value = json.loads(condition_value)
            except json.decoder.JSONDecodeError:
                condition_value = condition_value.replace('"', '').replace("'", '')

        if is_fat:
            condition_value = self.parse_rtype_value(condition_value)
        return is_fat, condition_value

    def parse_brackets(self, condition_str: str) -> list:
        """
        提取括号表达式转换为列表数据
        '((a>1 and 2) or b==3) and 4 or ((c>5 and 44) and d==8)'
        =>
        ['(a>1 and 2)',
            '((a>1 and 2) or b==3)',
            '(c>5 and 44)',
            '((c>5 and 44) and d==8)']

        Args:
            condition_str (str): '((a>1 and 2) or b==3) and 4 or ((c>5 and 44) and d==8)'

        Returns:
            list: _description_
        """
        b_l_list = []
        b_list = []
        if '(' not in condition_str or ')' not in condition_str:
            return [condition_str]
        for idx, item in enumerate(condition_str):
            if item == '(':
                b_l_list.append(idx)
            if item == ')':
                try:
                    l_idx = b_l_list[-1]
                except IndexError as err:
                    raise exceptions.BracketsError(condition_str) from err
                b_item = condition_str[l_idx:idx + 1]
                if re.findall(constants.BRACKETS_EMPTY_REGEX, b_item):
                    b_l_list.pop()
                    b_list.append(b_item)
        return b_list

    def find_brackets_content(
        self, condition_str: str
    ) -> typing.Optional[typing.List[str]]:
        """正则匹配到提取括号内的表达式内容
        '((a>2) or 3)' ==> ['(a>2) or 3']

        Args:
            condition_str (str): '((a>2) or 3)'

        Returns:
            typing.Optional[str]: ['(a>2) or 3']
        """
        find_list = re.findall(constants.BRACKETS_REGEX, condition_str)
        if find_list:
            return find_list

    def _replace_brackets(self, _string: str) -> str:
        """将对应的括号表达式替换为执行结果(True or False)

        Args:
            _string (str): '(1 or False) and True'

        Returns:
            str: 'True and True'
        """
        for key, value in self.match_cached.items():
            _string = _string.replace(key, str(value))
        return _string

    def _run_brackets(self, _brackets_str_list: list) -> None:
        """
        递归执行所有括号内的表达式得到结果，缓存起来，然后将对应的括号表达式替换为执行结果(True or False)
        (1 or False) and True and () ==> True and True and False

        Args:
            _brackets_str_list (list): (1 or False) and True and ()
        """
        for bra_str in _brackets_str_list:
            bra_str = self._replace_brackets(bra_str)
            _bra_str_list = self.parse_brackets(bra_str)
            _bra_str_list.sort(reverse=True)
            _find_bra_condition = None
            if len(_bra_str_list) == 1:
                _find_bra = self.find_brackets_content(_bra_str_list[0])
                if _find_bra:
                    # have brackets
                    _find_bra_condition = _find_bra[0]
                else:
                    _find_bra_condition = _bra_str_list[0]
                if _find_bra_condition:
                    # Cache conditional expression results
                    self.match_cached[_bra_str_list[0]] = self.match_condition(
                        _find_bra_condition
                    )
            else:
                self._run_brackets(_bra_str_list)

    def match_brackets(self, condition_str: str) -> str:
        """(1 or False) and True and () ==> True and True and False

        Args:
            condition_str (str): (1 or False) and True and ()

        Returns:
            str: True and True and False
        """
        full_condition_str = condition_str
        brackets_str_list = self.parse_brackets(condition_str)
        # 将小括号表达式排序到前面，减少括号计算
        brackets_str_list.sort(reverse=True)

        self._run_brackets(brackets_str_list)
        full_condition_str = self._replace_brackets(full_condition_str)
        self.log.debug('[match_brackets]: %s ==> %s', condition_str, full_condition_str)
        return full_condition_str

    def match_or(self, condition_str: str) -> bool:
        """
        匹配OR条件表达式
        Args:
            condition_str (list): '@fac.sql_type in ["select","update"] and @fun.char_length < 1000 and @fac.is_admin_user'

        Returns:
            bool: True：条件成立; False: 条件不成立
        """
        self.log.debug('[match_or condition_str]: %s', condition_str)
        _condition_str = condition_str.strip()
        if enums.ParserEnum.AND.value in _condition_str:
            _contidion_list = _condition_str.split(enums.ParserEnum.AND.value)
        else:
            _contidion_list = [_condition_str]
        for _c_string in _contidion_list:
            # 只要第一个条件为False，则返回
            if enums.ParserEnum.NOT_IN.value in _c_string:
                notin_list = _c_string.split(enums.ParserEnum.NOT_IN.value)
                match_notin_result = self.match_in_or_not(notin_list, type_='not in')
                if not match_notin_result:
                    return False
            elif enums.ParserEnum.IN.value in _c_string:
                # @fac.sql_type in ["select","update"]
                in_list = _c_string.split(enums.ParserEnum.IN.value)
                match_in_result = self.match_in_or_not(in_list, type_='in')
                if not match_in_result:
                    # stop match rule
                    return False
            else:
                re_match = re.search(constants.OPERATOR_REGEX, _c_string)
                if re_match:
                    # 如果有匹配上比较符号, 例如: @fac.sql_count > 1000
                    # @fun.is_char_lower(@fac.table_name)
                    match_span = re_match.span()
                    condition_name, condition_value = (
                        _c_string[:match_span[0]].strip(),
                        _c_string[match_span[-1]:].strip(),
                    )
                    lfat, condition_run_value = self.get_condition_value(condition_name)
                    rfat, condition_value = self.get_condition_value(condition_value)
                    _c_type_value = condition_value
                    try:
                        if lfat:
                            condition_type = type(condition_run_value)
                            _c_type_value = condition_type(condition_value)
                        elif rfat:
                            condition_value_type = type(condition_value)
                            condition_run_value = condition_value_type(
                                condition_run_value
                            )
                            _c_type_value = condition_value
                    except ValueError as err:
                        raise exceptions.TypeParseError(err)
                    if isinstance(_c_type_value, str):
                        _c_type_value = _c_type_value.replace('"', '').replace("'", '')
                    if isinstance(_c_type_value, str) and isinstance(
                        condition_run_value, str
                    ):
                        try:
                            _c_type_value = float(_c_type_value)
                            condition_run_value = float(condition_run_value)
                        except ValueError:
                            pass
                    if not constants.OPERATOR_MAP[
                        _c_string[match_span[0] : match_span[-1]]
                    ](condition_run_value, _c_type_value):
                        return False
                else:
                    # 没有比较符，例如: @fac.is_admin_user
                    _, condition_run_value = self.get_condition_value(_c_string)
                    if not condition_run_value:
                        return False
        return True

    def match_tree(self) -> bool:
        """匹配dsl所有流程条件

        Returns:
            bool: 默认返回True，即表示可以往下执行；False： 表示不可往下执行
        """
        matched = {'matched': None, 'result': None}
        parsed_str_list = self.dsl.parsed_string_list
        for condition_str_list in parsed_str_list:
            condition_str, then_str = condition_str_list
            if condition_str is True:
                result = self.dsl.chose_runner(then_str)
                matched['matched'] = condition_str_list
                matched['result'] = result
                self.matched = matched
                return result
            else:
                match_brackets_result = self.match_brackets(condition_str)
                match_result = self.match_condition(match_brackets_result)
                if match_result:
                    result = self.dsl.chose_runner(then_str)
                    matched['matched'] = condition_str_list
                    matched['result'] = result
                    self.matched = matched
                    return result
