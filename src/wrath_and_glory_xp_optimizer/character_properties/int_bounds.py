from __future__ import annotations

from typing import Any
from typing import Iterator
from typing import List
from typing import Optional
from typing import Union


class IntBounds:
    @property
    def min(self) -> Optional[int]:
        return self._values[0]

    @min.setter
    def min(self, min_value: Optional[int]) -> None:
        self._add_new_value(min_value, 0)

    @property
    def max(self) -> Optional[int]:
        return self._values[-1]

    @max.setter
    def max(self, max_value: Optional[int]) -> None:
        self._add_new_value(max_value, 1)

    def _add_new_value(self, val: Optional[int], position: int) -> None:
        self._values[position] = val
        self.sort()

    def __init__(self, min_value: Optional[int], max_value: Optional[int]) -> None:
        self._values: List[Optional[int]] = [min_value, max_value]
        self.sort()

    def __add__(self, other: Union[int, IntBounds]) -> IntBounds:
        if other is None:
            return IntBounds(None, None)

        if isinstance(other, int):
            other = IntBounds(min_value=other, max_value=other)

        if not isinstance(other, IntBounds):
            raise TypeError(
                f"unsupported operand type(s) for +: '{type(self).__name__}' and '{type(other).__name__}'"
            )

        values = []
        for self_val, other_val in zip(self._values, other._values):
            values.append(
                self_val + other_val
                if self_val is not None and other_val is not None
                else None
            )

        return IntBounds(*values)

    def __contains__(self, item: int) -> bool:
        return item in self.as_range()

    def __iter__(self) -> Iterator:
        return self._values.__iter__()

    def __str__(self) -> str:
        return self.__repr__().replace(type(self).__name__, "Integer ")

    def __repr__(self) -> str:
        return f"<{type(self).__name__} min={self.min}, max={self.max}>"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, IntBounds) and self._values == other._values

    def sort(self) -> None:
        if self.are_valid():
            self._values.sort()

    def as_range(self) -> range:
        if self.are_valid():
            return range(self.min, self.max + 1)
        return range(0, 0)

    def are_valid(self) -> bool:
        return None not in self._values
