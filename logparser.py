#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Piotrek Bronowski <piotr.bronowski@redembedded.com>
#
# Distributed under terms of the MIT license.

"""
Parse provided log file according to rules given in template file and write result file in desired format
"""
import csv
from optparse import OptionParser

import textfsm

def str_icomp(lhs, rhs):
    """compare two strins ignoring case"""
    try:
        return lhs.strip().upper() == rhs.strip().upper()
    except AttributeError:
        return lhs == rhs


class Parser(object):
    """
    parse log file
    """

    def __init__(self, options):
        self.input = options.input
        self.template = options.template
        self.output = options.output
        self.format = options.format
        self.header = []
        self.results = [list()]

    def write(self):
        """write data in given format"""
        with open(self.output, 'w') as output_file:
            if str_icomp(self.format, 'csv'):
                csv_writer = csv.writer(
                    output_file, delimiter=';', quoting=csv.QUOTE_MINIMAL, dialect=csv.excel, lineterminator='\n')
                csv_writer.writerow(self.header)
                for row in self.results:
                    csv_writer.writerow(row)
            elif str_icomp(self.format, 'jira'):
                line = '|'
                for element in self.header:
                    element = '|' + element + '|'
                    line += element
                line += '|\n'
                output_file.write(line)
                line = '|'
                for row in self.results:
                    for element in row:
                        element = element + '|'
                        line += element
                    line += '\n'
                    output_file.write(line)
                    line = '|'
            elif str_icomp(self.format, 'nice'):
                result = str(self.header) + '\n'
                for line in self.results:
                    result += str(line) + '\n'
                output_file.write(result)

    def parse(self):
        """parse input with rules applied in template"""
        # Open the template file, and initialise a new TextFSM object with it.
        fsm = textfsm.TextFSM(open(self.template))
        with open(self.input, 'r') as input_file:
            #the weakest part of this desing - you need to read the whole file
            self.results = fsm.ParseText(input_file.read())
        self.header = fsm.header
        self.write()

if __name__ == '__main__':
    OPTIONS_PARSER = OptionParser()
    OPTIONS_PARSER.add_option("-i", "--input",
                              action="store", type="string", dest="input", default="input.log",
                              help="read input to parse from IN_FILE", metavar="IN_FILE")
    OPTIONS_PARSER.add_option("-o", "--output",
                              action="store", type="string", dest="output", default="output.txt",
                              help="store parse result to OUT_FILE", metavar="OUT_FILE")
    OPTIONS_PARSER.add_option("-f", "--format",
                              action="store", type="string", dest="format", default="csv",
                              help="define output file FORMAT: csv, jira, nice [default: %default]", metavar="FORMAT")
    OPTIONS_PARSER.add_option("-t", "--template",
                              action="store", type="string", dest="template", default="siegemem_template",
                              help="read parsing rules from TEMPLATE", metavar="TEMPLATE")

    (OPTIONS, ARGS) = OPTIONS_PARSER.parse_args()
    try:
        PARSER = Parser(OPTIONS)
        PARSER.parse()
    except:
        OPTIONS_PARSER.print_help()
        raise
