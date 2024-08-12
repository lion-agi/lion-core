from typing import Type, TYPE_CHECKING
from lion_core.abc import BaseProcessor
from lion_core.form.base import BaseForm

from lion_core.session.session import Session
from lion_core.unit.unit_form import UnitForm

from lion_core.unit.process_parallel_chat import process_parallel_chat
from lion_core.unit.process_parallel_direct import process_parallel_direct

if TYPE_CHECKING:
    from lion_core.session.session import Session


class ParallelUnit(BaseProcessor):

    default_form: Type[BaseForm] = UnitForm

    def __init__(self, session: Session):
        self.session = session

    async def process_parallel_chat(self, **kwargs):
        return await process_parallel_chat(self.session, **kwargs)

    async def process_parallel_direct(self, **kwargs):
        return await process_parallel_direct(self.session, **kwargs)
