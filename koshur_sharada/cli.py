import argparse
import sys

from . import sharada_to_persoarabic, persoarabic_to_sharada


def main():
    parser = argparse.ArgumentParser(
        prog="koshur-sharada",
        description="Transliterate Kashmiri between Sharada and Perso-Arabic script.",
    )
    parser.add_argument(
        "direction",
        choices=["sh2pa", "pa2sh"],
        help="sh2pa = Sharada -> Perso-Arabic, pa2sh = Perso-Arabic -> Sharada",
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="Text to convert. If omitted, reads from stdin.",
    )
    parser.add_argument(
        "--diacritize",
        action="store_true",
        help=(
            "pa2sh only: run input through the Koshur Diacritizer model "
            "first, for under-diacritized Perso-Arabic text. Requires "
            "`pip install transformers torch`."
        ),
    )
    args = parser.parse_args()

    text = args.text if args.text is not None else sys.stdin.read().strip()

    if args.direction == "sh2pa":
        if args.diacritize:
            parser.error("--diacritize only applies to pa2sh (Sharada input is already unambiguous)")
        print(sharada_to_persoarabic(text))
    else:
        print(persoarabic_to_sharada(text, diacritize=args.diacritize))


if __name__ == "__main__":
    main()
