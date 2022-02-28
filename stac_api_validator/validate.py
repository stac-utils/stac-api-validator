import argparse
import logging
import sys
from validations import validate_api
import traceback


def parse_args(args):
    parser = argparse.ArgumentParser(description="STAC API Validation Suite")
    # todo: validate logging is one of these values
    parser.add_argument("--logging", default="INFO",
                        help="DEBUG, INFO, WARN, ERROR, CRITICAL")
    parser.add_argument("--root", help="STAC API Root / Landing Page URL")
    parser.add_argument(
        "--post",
        help="Also use POST method for requests",
        action=argparse.BooleanOptionalAction,
        default=True
    )

    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])

    logging.basicConfig(stream=sys.stdout, level=args.logging)

    if args.root is None:
        raise RuntimeError("No STAC API root URI provided")

    post = args.post

    print(f"Validating {args.root}", flush=True)

    try:
        (warnings, errors) = validate_api(args.root, post)
    except Exception as e:
        print(f"Failed.\nError {args.root}: {type(e)} {str(e)}")
        traceback.print_exc()
        return

    if warnings:
        print("warnings:")
    else:
        print("warnings: none")
    for warning in warnings:
        print(f"- {warning}")

    if errors:
        print("errors:")
    else:
        print("errors: none")
    for error in errors:
        print(f"- {error}")

    if errors:
        return 1
    else:
        return 0


if __name__ == "__main__":
    return_code = main()
    if return_code and return_code != 0:
        sys.exit(return_code)
