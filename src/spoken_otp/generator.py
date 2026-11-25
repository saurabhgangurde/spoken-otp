"""Select and uniformly sample the lowest-scoring pool of codes."""

from bisect import bisect_left
from dataclasses import dataclass, field
from math import log2
import secrets
from string import digits

from .profiles import ENGLISH_HEURISTIC, SpeechProfile

START = len(digits)
MAX_LENGTH = 12


@dataclass(frozen=True, slots=True)
class OTPGenerator:
    """Prepare a reusable uniform generator for a fixed length and profile."""

    length: int = 6
    min_candidates: int = 524_288
    profile: SpeechProfile = ENGLISH_HEURISTIC
    candidate_count: int = field(init=False)
    score_cutoff: int = field(init=False)
    _costs: tuple[tuple[int, ...], ...] = field(init=False, repr=False, compare=False)
    _counts: tuple[tuple[tuple[int, ...], ...], ...] = field(
        init=False, repr=False, compare=False
    )

    def __post_init__(self) -> None:
        if type(self.length) is not int or not 1 <= self.length <= MAX_LENGTH:
            raise ValueError(f"length must be an integer from 1 to {MAX_LENGTH}")
        space = len(digits) ** self.length
        if type(self.min_candidates) is not int or not 1 <= self.min_candidates <= space:
            raise ValueError(f"min_candidates must be an integer from 1 to {space} for this length")
        if not isinstance(self.profile, SpeechProfile):
            raise TypeError("profile must be a SpeechProfile")

        costs = tuple(
            tuple(
                penalty + self.profile.pair_penalties.get(previous + digit, 0)
                for digit, penalty in zip(digits, self.profile.digit_penalties)
            )
            for previous in digits
        ) + (self.profile.digit_penalties,)
        counts = _suffix_counts(costs, self.length)
        pool_sizes = counts[self.length][START]
        cutoff = bisect_left(pool_sizes, self.min_candidates)

        object.__setattr__(self, "_costs", costs)
        object.__setattr__(self, "_counts", counts)
        object.__setattr__(self, "score_cutoff", cutoff)
        object.__setattr__(self, "candidate_count", pool_sizes[cutoff])

    @property
    def entropy_bits(self) -> float:
        """Return the min-entropy in bits for one draw from this pool."""
        return log2(self.candidate_count)

    def generate(self) -> str:
        """Draw a code using the OS random source and preserve leading zeros."""
        rank = secrets.randbelow(self.candidate_count)
        budget = self.score_cutoff
        previous = START
        code = []
        for remaining in range(self.length - 1, -1, -1):
            for digit, cost in enumerate(self._costs[previous]):
                if cost > budget:
                    continue
                count = self._counts[remaining][digit][budget - cost]
                if rank < count:
                    code.append(digits[digit])
                    previous = digit
                    budget -= cost
                    break
                rank -= count
        return "".join(code)


def _suffix_counts(
    costs: tuple[tuple[int, ...], ...], length: int
) -> tuple[tuple[tuple[int, ...], ...], ...]:
    max_budget = max(map(max, costs)) * length
    # counts[remaining][previous digit][budget] counts suffixes costing at most budget.
    # The empty suffix costs zero, regardless of the preceding digit.
    counts = [((1,) * (max_budget + 1),) * len(costs)]
    for _ in range(length):
        shorter = counts[-1]
        counts.append(
            tuple(
                tuple(
                    sum(
                        shorter[digit][budget - cost]
                        for digit, cost in enumerate(row)
                        if cost <= budget
                    )
                    for budget in range(max_budget + 1)
                )
                for row in costs
            )
        )
    return tuple(counts)
