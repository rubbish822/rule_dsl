import logging

from .log import logger
logger.setLevel(logging.DEBUG)


def test_parse_string():
    from .parser import ConditionParser
    string = """if
                条件1
            then
                动作1
            elseif
                条件2
            then
                动作2
            else
                动作3
            end"""
    condition = ConditionParser(string)
    assert (condition.parsed_string_list) == [['条件1', '动作1'], ['条件2', '动作2'], [True, '动作3']]

    string = """if
            @fac.sql_type == select
            then
            @act.reject_execute
            else
            @act.allow_execute
            end
                """
    condition = ConditionParser(string)
    print(condition.parsed_string_list)
    assert condition.parsed_string_list == [['@fac.sql_type == select', '@act.reject_execute'], [True, '@act.allow_execute']]

    string = """
            if
            @fun.char_length > 1000
            then
            @act.reject_execute
            end
            """
    condition = ConditionParser(string)
    assert condition.parsed_string_list == [['@fun.char_length > 1000', '@act.reject_execute']]


def test_flow_and_in():
    from dsl.runner.mysql import MysqlDSL
    string = """
    if
    "select" == @fac.sql_type
    then
    @act.reject_execute '只能执行查询语句'
    elseif
    @fun.char_length > 1 and @fac.sql_type in ["select","insert"]
    then
    @act.allow_execute
    end
    """
    text = 'select * from table_name'
    rule = MysqlDSL(string, text)
    assert rule.match_tree() is False
    assert rule.end_msg == (False, "'只能执行查询语句'")


def test_flow_and():
    from dsl.runner.mysql import MysqlDSL
    string = """
    if
    @fun.char_length > 1 and @fac.sql_type == "select"
    then
    @act.allow_execute
    end
    """
    text = 'select * from table_name2'
    rule = MysqlDSL(string, text)
    assert rule.match_tree() is True


def test_flow_and_more():
    from dsl.runner.mysql import MysqlDSL
    string = """
    if
    @fun.char_length > 1 and @fac.sql_type == "select" and @fac.sql_type in ["delete"]
    then
    @act.allow_execute
    end
    """
    text = 'select * from table_name3'
    rule = MysqlDSL(string, text)
    assert rule.match_tree() is None


def test_flow_and_in_notin():
    from dsl.runner.mysql import MysqlDSL
    string = """
    if
    @fun.char_length > 1 and @fac.sql_type == "select" and @fac.sql_type not in ["delete"]
    then
    @act.allow_execute
    end
    """
    text = 'select * from table_name4'
    rule = MysqlDSL(string, text)
    assert rule.match_tree() is True


def test_flow_only():
    from dsl.runner.mysql import MysqlDSL
    string = """
    if
    @fun.is_admin_user
    then
    @act.allow_execute
    end
    """
    text = 'select * from table_name5'
    rule = MysqlDSL(string, text)
    assert rule.match_tree() is None


def test_flow_mul_flow():
    from dsl.runner.mysql import MysqlDSL
    string = """
    if
    false and 100990 < @fac.char_length and @fun.sql_type in @fac.can_run_type
    then
    @act.allow_execute
    elseif
    @fun.sql_type != "select" and @fun.is_admin_user
    then
    @act.allow_execute
    elseif
    @fac.char_length >= 100
    then
    @act.allow_execute
    elseif
    @fun.is_char_lower("UPPER")
    then
    @act.allow_execute
    elseif
    false and @fun.is_char_lower(@fac.sql_type) or false
    then
    @act.allow_execute
    else
    @act.reject_execute
    end
    """
    text = 'select * from table_name5'
    rule = MysqlDSL(string, text, log=logger)
    assert rule.match_tree() is False


def test_flow_or():
    from dsl.runner.mysql import MysqlDSL
    string = """
    if
    @fun.char_length < 1 and @fac.sql_type == "select2" or "" or @fac.sql_type not in ["delete"]
    then
    @act.allow_execute
    end
    """
    text = 'select * from table_name4'
    rule = MysqlDSL(string, text)
    assert rule.match_tree() is True


def test_white():
    from dsl.runner.mysql import MysqlDSL
    string = """
    if
    true and 1
    then
    true
    end
    """
    md = MysqlDSL(string, 'select * from table_name', allow_no_params=True, log=logger)
    assert md.match_tree()


def test_space():
    from dsl.runner.mysql import MysqlDSL
    string = """
    if
    @fac.char_length <= 100
    then
    true
    end
    """
    md = MysqlDSL(string, 'select * from table_name', allow_no_params=True, log=logger)
    assert md.match_tree() is True


def test_rtype_value():
    from dsl.runner.mysql import MysqlDSL
    string = """
    if
    44 == @fac.char_length
    then
    @act.allow_execute
    elseif
    @fac.sql_type not in ["select"] and 
    then
    @act.allow_execute allow select
    elseif
    @fac.test_dict == {"a":1,"b":2}
    then
    @act.allow_execute dict ok
    else
    @act.reject_execute
    end
    """
    md = MysqlDSL(string, 'select * from table_name', allow_no_params=True, log=logger)
    md.match_tree()
    assert md.end_msg == (True, 'dict ok')


def test_trackets():
    from dsl.runner.mysql import MysqlDSL
    # string = """
    # if
    # (@fac.sql_type not in ["select"] or @fac.char_length > 1) or @fun.is_char_lower(@fac.sql_type) or (1 and 2)
    # then
    # @act.allow_execute
    # end
    # """
    string = """
    if
    (1 and False) and 4 or (False or 5) and 4 > 20
    then
    @act.allow_execute
    elseif
    (1 or False) and True and ()
    then
    @act.allow_execute 1
    else
    @act.reject_execute reject
    end
    """
    md = MysqlDSL(string, 'select * from table_name', allow_no_params=True, log=logger)
    md.match_tree()
    assert md.end_msg == (False, 'reject')


def test_regex():
    from dsl.runner.mysql import MysqlDSL
    string = """
    if
    "idx_aa" matchs "idx_\\w+"
    then
    @act.allow_execute success
    else
    @act.reject_execute failed
    end
    """
    md = MysqlDSL(string, 'select * from table_name')
    md.match_tree()
    assert md.end_msg == (True, 'success')


# pytest dsl/tests.py -o log_cli=true
