#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Piotrek Bronowski <piotr.bronowski@redembedded.com>
#
# Distributed under terms of the MIT license.

"""
Parses provided log file according to rules given in template file and writes result file in desired format
"""

import textfsm
import csv
from optparse import OptionParser

def str_icomp(a, b):
    try:
        return a.strip().upper() == b.strip().upper()
    except AttributeError:
        return a == b

class Parser:
    """
    Parses log file.
    """
    def __init__(self, options):
        self.input = options.input
        self.template = options.template
        self.output = options.output
        self.format = options.format
        self.header = []
        self.results = [list()]

    def write(self):
        with open(self.output, 'w') as csvfile:
            if str_icomp(self.format, 'csv'):
                csvWriter = csv.writer(
                    csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL, dialect=csv.excel, lineterminator='\n')
                csvWriter.writerow(self.header)
                for row in self.results:
                    csvWriter.writerow(row)
            elif str_icomp(self.format, 'jira'):
                csvWriter = csv.writer(
                    csvfile, delimiter='|', quoting=csv.QUOTE_MINIMAL, dialect=csv.excel, lineterminator='|\n')
                for field in self.header:
                    field = '|' + field + '|'
                csvWriter.writerow(self.header)
                for row in self.results:
                    row[0] = '|' + row[0]
                    csvWriter.writerow(row)

    def parse(self):
        # Open the template file, and initialise a new TextFSM object with it.
        fsm = textfsm.TextFSM(open(self.template))
        with open(self.input, 'r') as input_file:
            self.results = fsm.ParseText(input_file.read())
        self.header = fsm.header
        self.write()

if __name__ == '__main__':
    options_parser = OptionParser()
    options_parser.add_option("-i", "--input",
                              action="store", type="string", dest="input", default="input.log",
                              help="reads input to parse from FILE", metavar="FILE")
    options_parser.add_option("-o", "--output",
                              action="store", type="string", dest="output", default="output.txt",
                              help="reads input to parse from FILE", metavar="FILE")
    options_parser.add_option("-f", "--format",
                              action="store", type="string", dest="format", default="csv",
                              help="define output file FORMAT: csv, jira, nice [default: %default]", metavar="FORMAT")
    options_parser.add_option("-t", "--template",
                              action="store", type="string", dest="template", default="siegemem_template",
                              help="reads parsing rules from template FILE", metavar="FILE")

    options_parser.set_usage('usage: logparser.py [options]')
    (options, args) = options_parser.parse_args()
    try:
        parser = Parser(options)
        parser.parse()
    except:
        options_parser.print_help()
        raise
