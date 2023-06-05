from dsl.utils import fac, fun


class SQLCommonFAT:
    @fac(title='SQL大类', enabled=True)
    def sql_type(self) -> str:
        return self.text.sql_type

    @fac(title='可以执行的SQL类型')
    def can_run_type(self) -> bool:
        return self.text.can_run_type

    @fac(title='是否是管理员')
    def is_admin_user(self) -> bool:
        return getattr(self.text.user, 'pk', None) == 'admin'

    @fun(rtype='int')
    def char_length(self) -> int:
        return len(self.text.value)

    @fun(title='是否是小写字符')
    def is_char_lower(self, value: str) -> bool:
        """判断字符串是否是小写

        Args:
            value (str): 1. @fun.is_char_lower(‘dms’) // true

                         2. @fun.is_char_lower(@fac.table_name) // 返回true的话，表名都是小写。

        """
        if value.startswith('@fac.'):
            value = getattr(self, value)()
        return value.islower()
