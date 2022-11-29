#! /usr/bin/env python3
import re
import sys
import rsm
from pathlib import Path
from argparse import ArgumentParser
from textwrap import indent

TEMPLATE = """

def {test_name}():
    compare_have_want(
        have=\"\"\"
{source}
        \"\"\",
        want=\"\"\"
{target}
        \"\"\",
    )
"""
ROOT_TEST_PATH = Path(rsm.__file__).parent.parent / 'tests'


def main(file_path, test_path, test_name, handrails=False):
    """Turn a text file into a test."""
    out_path = ROOT_TEST_PATH / test_path
    assert out_path.exists()

    with open(out_path, encoding='utf-8') as file:
        current_tests = file.read()
    if re.search(f'^def {test_name}\(', current_tests, flags=re.MULTILINE):
        raise ValueError('Test with that name already exists')

    with open(file_path, encoding='utf-8') as file:
        source = file.read()
    target = rsm.render(source, handrails=handrails, treesitter=True)

    with open(out_path, 'a', encoding='utf-8') as file:
        file.write(
            TEMPLATE.format(
                test_name=test_name,
                source=indent(source.strip(), '        '),
                target=indent(target.strip(), '        '),
            )
        )

    sys.exit(0)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('file_path', help='path to RSM file')
    parser.add_argument(
        'test_path', help='path to test module relative to rsm/rsm/tests'
    )
    parser.add_argument('test_name', help='name of new test')
    parser.add_argument(
        '-r',
        '--handrails',
        help='with handrails',
        action='store_true',
        default=False,
    )
    args = parser.parse_args()
    main(args.file_path, args.test_path, args.test_name, args.handrails)
