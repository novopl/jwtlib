import abc
from typing import Generic, Optional, TypeVar

from .types import TokenPayload


T = TypeVar('T')


class UserAdapterBase(abc.ABC, Generic[T]):
    @abc.abstractmethod
    def payload_for_user(self, account: T) -> TokenPayload:
        ...

    @abc.abstractmethod
    def user_for_payload(self, payload) -> Optional[T]:
        ...
