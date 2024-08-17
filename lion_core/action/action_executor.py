"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from lion_core.abc import Action, BaseExecutor, Observable
from lion_core.generic.pile import Pile, pile
from lion_core.generic.progression import prog, Progression

from lion_core.action.status import ActionStatus


class ObservableAction(Action, Observable):
    ...
    

class ActionExecutor(BaseExecutor):

    def __init__(self, **kwargs) -> None:
        self.processor_config = kwargs
        self.pile: Pile = pile(item_type=ObservableAction)
        self.pending: Progression = prog()

    async def append(self, action: ObservableAction):
        self.pile.append(action)
        self.pending.append(action)

    @property
    def pending_action(self) -> Pile:
        return pile(
            [i for i in self.pile if i.status == ActionStatus.PENDING],
        )

    @property
    def completed_action(self) -> Pile:
        return pile(
            [i for i in self.pile if i.status == ActionStatus.COMPLETED],
        )

    def __contains__(self, action):
        return action in self.pile

    def __iter__(self):
        return iter(self.pile)
