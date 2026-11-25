"""Command-line entry point for spoken-otp."""

import argparse

from .generator import OTPGenerator


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate one decimal code using a speech profile.")
    parser.add_argument("--length", type=int, default=6, help="number of digits (default: 6)")
    parser.add_argument(
        "--min-candidates",
        type=int,
        default=524_288,
        help="minimum number of possible codes (default: 524288)",
    )
    args = parser.parse_args()
    try:
        generator = OTPGenerator(length=args.length, min_candidates=args.min_candidates)
    except ValueError as error:
        parser.error(str(error))
    print(generator.generate())


if __name__ == "__main__":
    main()
