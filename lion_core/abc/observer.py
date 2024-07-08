from abc import ABC, abstractmethod
from .concept import AbstractObserver


class Manager(AbstractObserver, ABC):
    pass

class BaseAgent(AbstractObserver, ABC):
    pass

class BaseWorker(AbstractObserver, ABC):
    pass

class BaseExecutor(AbstractObserver):
    
    @abstractmethod
    async def execute(self, *args, **kwargs):
        pass
    