import argparse
import logging
import sys
import os
from validations import validate_api


def parse_args(args):
    parser = argparse.ArgumentParser(description='STAC API Validation Suite')
    # todo: validate logging is one of these values
    parser.add_argument('--logging', default='INFO',
                        help='DEBUG, INFO, WARN, ERROR, CRITICAL')
    parser.add_argument('--root', help='Landing Page URI',
                        default=os.getenv('STAC_API_ROOT_URI', None))

    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])

    logging.basicConfig(stream=sys.stdout, level=args.logging)

    if args.root is None:
        raise RuntimeError('No STAC API root URI provided')

    (warnings, errors) = validate_api(args.root)

    print(f"warnings: {warnings}")
    print(f"errors: {errors}")

    if errors:
        return 1
    else:
        return 0


if __name__ == "__main__":
    return_code = main()
    if return_code and return_code != 0:
        sys.exit(return_code)
