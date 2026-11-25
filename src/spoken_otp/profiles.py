"""Score digit strings using per-digit and directed adjacent-pair penalties."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from string import digits
from types import MappingProxyType

MAX_PENALTY = 10


@dataclass(frozen=True, slots=True)
class SpeechProfile:
    """A fixed scoring profile. Lower scores receive priority."""

    digit_penalties: tuple[int, ...] = (0,) * 10
    pair_penalties: Mapping[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        digit_penalties = tuple(self.digit_penalties)
        pair_penalties = dict(self.pair_penalties)
        if len(digit_penalties) != len(digits):
            raise ValueError("digit_penalties must have ten entries, in order from 0 to 9")
        if any(
            not isinstance(pair, str) or len(pair) != 2 or not all(digit in digits for digit in pair)
            for pair in pair_penalties
        ):
            raise ValueError("pair_penalties keys must be strings of two ASCII digits")
        if any(
            type(penalty) is not int or not 0 <= penalty <= MAX_PENALTY
            for penalty in (*digit_penalties, *pair_penalties.values())
        ):
            raise ValueError(f"penalties must be integers from 0 to {MAX_PENALTY}")

        object.__setattr__(self, "digit_penalties", digit_penalties)
        object.__setattr__(self, "pair_penalties", MappingProxyType(pair_penalties))

    def score(self, code: str) -> int:
        """Return the sum of the digit and adjacent-pair penalties."""
        if not isinstance(code, str) or not code or not all(digit in digits for digit in code):
            raise ValueError("code must be a nonempty string of ASCII digits")
        digit_cost = sum(self.digit_penalties[int(digit)] for digit in code)
        pair_cost = sum(
            self.pair_penalties.get(first + second, 0)
            for first, second in zip(code, code[1:])
        )
        return digit_cost + pair_cost


ENGLISH_HEURISTIC = SpeechProfile(
    digit_penalties=(0, 2, 0, 2, 1, 2, 2, 0, 0, 2),
    pair_penalties={**{digit * 2: 1 for digit in digits}, "82": 2},
)
