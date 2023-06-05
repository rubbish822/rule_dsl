import logging
from dataclasses import dataclass

from . import common

logger = logging.getLogger(__name__)


@dataclass
class BaseText:
    value: str
    user: common.User
