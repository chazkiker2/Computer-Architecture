#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

if __name__ == '__main__':
    cpu = CPU()

    cpu.load()
    cpu.run()
