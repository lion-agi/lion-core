from lion_core.abc import AbstractSpace, Observable, Temporal
from lion_core.sys_util import SysUtil


class BaseSession(AbstractSpace, Observable, Temporal):

    def __init__(self) -> None:
        self.ln_id = SysUtil.id()
        self.timestamp = SysUtil.time(type_="timestamp")
