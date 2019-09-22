# -*- coding: utf-8 -*-

# stdlib imports
from typing import Any, Callable, Dict, Sequence, Tuple, Union
from types import FunctionType

JsonDict = Dict[str, Any]
PlainType = Union[str, int, float, bool]
Decorator = Callable[[FunctionType], FunctionType]
