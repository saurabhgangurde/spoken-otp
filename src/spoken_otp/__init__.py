"""Generate decimal one-time codes with a configurable speech score."""

from .generator import OTPGenerator
from .profiles import ENGLISH_HEURISTIC, SpeechProfile

__all__ = ["ENGLISH_HEURISTIC", "OTPGenerator", "SpeechProfile"]
