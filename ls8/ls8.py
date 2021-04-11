#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *


def main():
    cpu = CPU()

    try:
        seed_file = sys.argv[1]
    except IndexError:
        seed_file = "examples/print8.ls8"
        print(f"No argument given, defaulting to {seed_file}")

    cpu.load(seed_file)
    cpu.run()


if __name__ == '__main__':
    main()
