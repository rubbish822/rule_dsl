from ..dsl import BaseCommonDSL
from ..text_parser import BaseText
from ..utils import fac
from . import SQLCommonFAT


class MysqlText(BaseText):
    @property
    def sql_type(self) -> str:
        grammar_upper = self.value.upper()
        sql_type = None
        if 'SELECT' in grammar_upper:
            sql_type = 'select'
        elif 'UPDATE' in grammar_upper:
            sql_type = 'update'
        elif 'DELETE' in grammar_upper:
            sql_type = 'delete'
        elif 'INSERT' in grammar_upper:
            sql_type = 'insert'
        return sql_type

    @property
    def can_run_type(self) -> list:
        return ['select']


class MysqlDSL(BaseCommonDSL, SQLCommonFAT):
    type_ = 'mysql'
    text_parser = MysqlText

    @fac(rtype='dict')
    def test_dict(self) -> dict:
        return {'a': 1, 'b': 2}
