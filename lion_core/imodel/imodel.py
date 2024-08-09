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

from abc import abstractmethod
from lion_core.abc import BaseiModel
from lion_core.generic.element import Element


class iModel(Element, BaseiModel):

    async def update_status(self, *args, **kwargs) -> None:
        """
        Update the status of the iModel.

        Args:
            status (str): The status of the iModel.
            state (str): The state of the iModel.

        Returns:
            None
        """
        pass

    @abstractmethod
    async def chat(self, input_, endpoint="chat/completions", **kwargs): ...


__all__ = ["iModel"]
