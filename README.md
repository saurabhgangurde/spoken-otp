# spoken-otp

Generate decimal one-time codes intended to be read aloud. Pick a speech scoring profile and a minimum code space. The generator gives priority to lower-scoring codes and draws uniformly from the selected pool using the operating system's random source.

The project started with a question about misheard ride pickup PINs in Bengaluru traffic. It ships an **experimental English profile**. Whether it reduces errors in traffic, on phone calls, or for any given accent is an open research question.

## Install

Requires Python 3.10 or newer. The package has no runtime dependencies.

```sh
python -m pip install git+https://github.com/saurabhgangurde/spoken-otp.git
```

## Use

```python
from spoken_otp import OTPGenerator

generator = OTPGenerator(length=6, min_candidates=2**19)
code = generator.generate()  # Six ASCII digits as a string, including leading zeros.

print(generator.candidate_count)
print(generator.entropy_bits)
```

Reuse the generator for a given configuration. It counts the candidate pool once and uses a fresh random draw for each code.

```sh
spoken-otp --length 6 --min-candidates 524288
```

The CLI prints a code to standard output for local use.

## How generation works

1. Score each code conceptually by adding per-digit and adjacent-pair penalties. A lower score is preferred.
2. Find the lowest score cutoff that admits at least `min_candidates` codes. Include every code tied at that cutoff.
3. Draw a uniformly random rank with [Python's `secrets.randbelow`](https://docs.python.org/3/library/secrets.html#secrets.randbelow). Count suffixes by remaining length, previous digit, and remaining penalty budget to map the rank to a code without enumerating the code space.

For a pool of `N` codes, a particular code has probability `1/N` and a single draw has min-entropy `log2(N)`. An impossible floor raises `ValueError`. Setting `min_candidates=10**length` yields ordinary uniform decimal codes. To keep at least the 10,000 possibilities of a uniform four-digit code while applying speech scoring, use `OTPGenerator(length=5, min_candidates=10_000)`.

An application's verification system is responsible for expiration, single use, attempt limits, and binding each code to the intended transaction. Treat active codes as secrets and keep them out of logs.

## Custom profiles

Use penalties from 0 to 10. Digit penalties are ordered from zero through nine. Pair penalties are directional and unspecified pairs cost zero. Code lengths from 1 to 12 are supported.

```python
from spoken_otp import OTPGenerator, SpeechProfile

profile = SpeechProfile(pair_penalties={"82": 2})
generator = OTPGenerator(length=6, min_candidates=2**19, profile=profile)
assert profile.score("082") == 2
```

The bundled profile favors 0, 2, 7, and 8, assigns a smaller penalty to 4 than to the other digits, and penalizes repeats and the sequence 8 followed by 2. See the [evaluation guide](docs/evaluation.md) for a protocol to test the profile or build a better one.

## Contribute

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
```

For a profile contribution, describe the speaking and listening conditions it targets and share results from synthetic or consenting test sessions.

[MIT license](LICENSE)
