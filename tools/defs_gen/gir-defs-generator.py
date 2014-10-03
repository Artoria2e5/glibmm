#!/usr/bin/env python

import sys

from girparser import GirParser
from girprinter import GirPrinter

# Possible types:
# function
# callback
# union
# constant
# alias
# class
# record
# interface
# bitfield
# enumeration


def main(args):
    if len(args) < 2:
        print('Must specify one input filename')
        return -1

    parser = GirParser()
    parser.parse_file(args[1])
    printer = GirPrinter(parser)

    printer.print_enumerations()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
