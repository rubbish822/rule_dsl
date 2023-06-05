from ..dsl import BaseCommonDSL
from ..text_parser import BaseText
from ..utils import fac


class RedisText(BaseText):
    pass


class RedisDSL(BaseCommonDSL):
    type_ = 'redis'
    text_parser = RedisText

    @fac
    def cmd_type(self):
        pass

    @fac
    def user_is_admin(self):
        return self.text.user.pk == 'admin'
