""" Common types used in jwtlib. """

from typing import Any, Callable, Dict, Union


JsonDict = Dict[str, Any]
PlainType = Union[str, int, float, bool]
Decorator = Callable[..., Any]
