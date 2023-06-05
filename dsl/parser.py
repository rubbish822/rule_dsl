import functools

from . import log
from . import exceptions
from . import enums


class Parser:
    def __init__(self, grammar: str):
        self.grammar = grammar
        self.log = log.dsl_parser_log

    def parse_string(self):
        raise NotImplementedError(
            "subclasses of Grammar must provide a parse_string() method"
        )

    @functools.cached_property
    def parsed_string_list(self):
        return self.parse_string()


class ConditionParser(Parser):
    """
    example:
    ```
    1. str:
        '''
        if
        "string"
        then
        @act.allow_execute "allow test ok"
        end
        '''
    2. int or float:
        '''
        if
        1 > 0 and 3.5 > 1
        then
        @act.allow_execute
        end
        '''
    3. list or dict:
        '''
        if
        "a" in ["a","b"] or "address" not in {"name": "tom", "age": 18}
        then
        @act.allow_execute
        end
        '''
    4. regex:
        ```
        if
        "idx_aa" matchs "idx_\\w+"
        then
        @act.allow_execute
        end
        ```
    ```

    Args:
        grammar (str):  if
                        Condition 1
                        then
                            Action 1
                        elseif
                            Condition 2
                        then
                            Action 2
                        else
                            Action 3
                        end

    """

    rule_map = {
        "if": ["then"],
        "then": ["elseif", "else", "end"],
        "elseif": ["then"],
        "else": ["end"],
        "end": [],
    }

    def parse_string(self) -> list:
        """parse string to list
        ```
        1. str:
            '''
            if
            "string"
            then
            @act.allow_execute "allow test ok"
            end
            '''
        2. int or float:
            '''
            if
            1 > 0 and 3.5 > 1
            then
            @act.allow_execute
            end
            '''
        3. list or dict:
            '''
            if
            "a" in ["a","b"] or "address" not in {"name": "tom", "age": 18}
            then
            @act.allow_execute
            end
            '''
        4. regex:
            ```
            if
            "idx_aa" matchs "idx_\\w+"
            then
            @act.allow_execute
            end
            ```
        ```

        Args:
            grammar (str):  if
                            Condition 1
                            then
                                Action 1
                            elseif
                                Condition 2
                            then
                                Action 2
                            else
                                Action 3
                            end

        Returns:
            list: [['Condition 1', 'Action 1'], ['Condition 2', 'Action 2'], [True, 'Action 3']]
        """
        grammar = self.grammar
        self.log.debug("Grammar: %s", grammar)
        parsed_string_list = []
        parsed_string_list_pos = 0
        grammar_list = grammar.strip().split("\n")
        grammar_list_length = len(grammar_list) - 1
        last_str = None
        next_dsl_idx = 2
        dsl_map = self.rule_map
        for idx, string in enumerate(grammar_list):
            _string = string.strip()
            if idx == 0 and _string != enums.DSL.IF.value:
                raise exceptions.DSLError(
                    "[Grammar error]: The first character should be [if]"
                )
            if idx == grammar_list_length and _string != enums.DSL.END.value:
                raise exceptions.DSLError(
                    "[Grammar error]: The last character should be [end]"
                )
            if not last_str:
                if idx == 0:
                    last_str = enums.DSL.IF.value
                else:
                    raise exceptions.DSLError("Grammar error")
            else:
                if idx == next_dsl_idx:
                    # check dsl
                    if _string not in dsl_map[last_str]:
                        raise exceptions.DSLError(
                            f"[Grammar error]: Line {idx} characters: [{_string}] should be one of {dsl_map[last_str]}"
                        )
                    else:
                        last_str = _string
                        next_dsl_idx += 2
                else:
                    # add str to list
                    if idx == grammar_list_length:
                        break
                    if parsed_string_list_pos == 0:
                        if len(parsed_string_list) == 0:
                            parsed_string_list.append([_string])
                        else:
                            parsed_string_list[0].append(_string)
                        if len(parsed_string_list[parsed_string_list_pos]) == 2:
                            parsed_string_list_pos = 1
                    else:
                        if len(parsed_string_list) == parsed_string_list_pos:
                            parsed_string_list.append([_string])
                        else:
                            parsed_string_list[parsed_string_list_pos].append(_string)
                            if len(parsed_string_list[parsed_string_list_pos]) == 2:
                                parsed_string_list_pos += 1

        last_parsed_string_list = parsed_string_list[len(parsed_string_list) - 1]
        if len(last_parsed_string_list) == 1:
            last_parsed_string_list.insert(0, True)
        self.log.debug("[Grammar parsed_string_list]: %s", parsed_string_list)
        return parsed_string_list
