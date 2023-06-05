from ..dsl import BaseCommonDSL
from ..text_parser import BaseText
from ..utils import fac
from . import SQLCommonFAT


class PgText(BaseText):
    pass


class PgDSL(BaseCommonDSL, SQLCommonFAT):
    type_ = 'postgres'

    @fac(title='是否是管理员')
    def is_admin_user(self) -> bool:
        return self.text.user == 'admin'
