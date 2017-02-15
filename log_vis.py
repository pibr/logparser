#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Piotrek Bronowski <piotr.bronowski@redembedded.com>
#
# Distributed under terms of the MIT license.
"""
This script allows to visualise relevant perfomance information from logs
"""
from __future__ import print_function

import getopt
import sys
from optparse import OptionParser

import matplotlib  # only needed to determine Matplotlib version number
import matplotlib.pyplot as plt
import numpy
import pandas as pd
import pylab
from pandas import DataFrame, read_csv
from pint import UnitRegistry

matplotlib.style.use('ggplot')
matplotlib.rcParams['agg.path.chunksize'] = 10000


class DataRenderer(object):
    inputfile = str()
    iterations = 1
    comparator = str()
    filter_column_name = str()
    filter_values = list()
    ax = None
    index_column_name = str()
    index_unit = str()
    values_unit = str()
    values_column_name = str()

    ureg = UnitRegistry()

    @staticmethod
    def read_from_template():
        pass

    @staticmethod
    def __label():
        """Produces a label for graph"""
        if DataRenderer.values_unit != '':
            return DataRenderer.values_column_name + ' ' + '[' + DataRenderer.values_unit + ']'
        else:
            return DataRenderer.values_column_name

    @staticmethod
    def __finalise():
        plt.xlabel(DataRenderer.index_column_name)
        plt.ylabel(DataRenderer.__label())
        pylab.show()

    @staticmethod
    def __convert(df, col_name, unit):
        if unit == 'datetime':
            df[col_name] = pd.to_datetime(df[
                col_name], infer_datetime_format=True)
        else:
            df[col_name] = pd.to_numeric(df[col_name])

    @staticmethod
    def visualise(counter, data_frame):
        if counter == 0:
            DataRenderer.__finalise()
            return
        else:
            extream_value = data_frame.loc[
                data_frame[DataRenderer.values_column_name].idxmax()]
            value = extream_value[DataRenderer.filter_column_name]
            name = str(extream_value['Name']) + ' ' + '[' + str(value) + ']'
            # for col in T.units:
            #    extream_value[col] = Common.inUnits(
            #        extream_value[col], col, Common.values_unit)
            print(extream_value)
            df_filtered = data_frame.loc[
                data_frame[DataRenderer.filter_column_name] == value]
            df_new = data_frame.loc[
                data_frame[DataRenderer.filter_column_name] != value]
            if DataRenderer.index_unit == 'datetime':
                df_filtered[DataRenderer.index_column_name] = df_filtered[
                    DataRenderer.index_column_name].apply(pd.to_datetime)
            if DataRenderer.values_unit == 'counter':
                df_filtered[DataRenderer.values_column_name] = pd.to_numeric(df_filtered[
                    DataRenderer.values_column_name])
            DataRenderer.ax = df_filtered.plot(
                ax=DataRenderer.ax, label=name, x=DataRenderer.index_column_name, y=DataRenderer.values_column_name)
            DataRenderer.visualise(counter - 1, df_new)

    @staticmethod
    def visualise_values(values, data_frame):
        if not values:
            DataRenderer.__finalise()
            return
        else:
            value = values[0]
            values.remove(value)
            df_filtered = data_frame.loc[
                data_frame[DataRenderer.filter_column_name] == value]
            extream_value = None
            if DataRenderer.comparator == 'max':
                extream_value = df_filtered.loc[
                    df_filtered[DataRenderer.values_column_name].idxmax()]
                print(extream_value)
            #name = str(extream_value[
            #           Common.filter_column_name]) + ' ' + '[' + str(value) + ']'
            # for col in T.units:
            #    extream_value[col] = Common.inUnits(extream_value[col], col, T.units)
            print(extream_value)
            df_new = data_frame.loc[
                data_frame[DataRenderer.filter_column_name] != value]
            DataRenderer.__convert(
                df_filtered, DataRenderer.index_column_name, DataRenderer.index_unit)
            DataRenderer.__convert(
                df_filtered, DataRenderer.values_column_name, DataRenderer.values_unit)
            # if Common.index_unit == 'datetime':
            #    df_filtered[Common.index_column_name] = pd.to_datetime(df_filtered[
            #        Common.index_column_name], infer_datetime_format=True)
            # if Common.values_unit == 'counter':
            #    df_filtered[Common.values_column_name] = df_filtered[
            #        Common.values_column_name].apply(pd.to_numeric)
            DataRenderer.ax = df_filtered.plot(
                ax=DataRenderer.ax, label=value, x=DataRenderer.index_column_name, y=DataRenderer.values_column_name,)
            DataRenderer.visualise_values(values, df_new)

    @staticmethod
    def process_input():
        data_frame = pd.read_csv(DataRenderer.inputfile, delimiter=';')
        if not DataRenderer.filter_values:
            DataRenderer.visualise(DataRenderer.iterations, data_frame)
        else:
            DataRenderer.visualise_values(DataRenderer.filter_values, data_frame)


def main(options):
    """Entry point"""
    if options.template != '':
        DataRenderer.read_from_template()
    else:
        DataRenderer.inputfile = options.input
        DataRenderer.iterations = int(options.plots_no.split(',')[0].strip())
        if options.plots_no.split(',')[1]:
            DataRenderer.comparator = options.plots_no.split(',')[1].strip()
        else:
            DataRenderer.comparator = 'max'
        DataRenderer.index_column_name = options.index_column
        filter_col = map(str.strip, options.filter.split(','))
        DataRenderer.filter_column_name = filter_col.pop(0)
        DataRenderer.filter_values = filter_col
        DataRenderer.values_column_name = options.values_column
        DataRenderer.index_unit = map(str.strip, options.units.split(','))[0]
        DataRenderer.values_unit = map(str.strip, options.units.split(','))[1]

    print('Matplotlib version ' + matplotlib.__version__)
    print ('Input file is ', DataRenderer.inputfile)
    DataRenderer.process_input()
    print ('Operation successfully completed!')

if __name__ == "__main__":
    OPTIONS_PARSER = OptionParser()
    OPTIONS_PARSER.add_option("-i", "--input",
                              action="store", type="string", dest="input", default="input.log",
                              help="reads input to parse from CSV_FILE", metavar="CSV_FILE")
    OPTIONS_PARSER.add_option("-o", "--output",
                              action="store", type="string", dest="output", default="output.txt",
                              help="stores output to FILE", metavar="FILE")
    OPTIONS_PARSER.add_option("-n", "--num_plots",
                              action="store", type="string", dest="plots_no", default="1,max",
                              help="sets number of plots to draw", metavar="PLOTS")
    OPTIONS_PARSER.add_option("-f", "--filter",
                              action="store", type="string", dest="filter", default=",",
                              help="define column for filtering and FILTER value separated by comma [default: %default]"
                              , metavar="FILTER")
    OPTIONS_PARSER.add_option("-y", "--y_values",
                              action="store", type="string", dest="values_column", default="",
                              help="defines column with values to plot separated by comma", metavar="VALUES_COLUMN")
    OPTIONS_PARSER.add_option("-t", "--template",
                              action="store", type="string", dest="template", default="",
                              help="reads visualisation rules from TEMPLATE file", metavar="TEMPLATE")
    OPTIONS_PARSER.add_option("-x", "--index_column",
                              action="store", type="string", dest="index_column", default="Timestamp",
                              help="defines indexing column INDEX_COLUMN", metavar="INDEX_COLUMN")
    OPTIONS_PARSER.add_option("-u", "--units",
                              action="store", type="string", dest="units", default=",",
                              help="defines units of x and y axis separated by comma", metavar="UNITS")

    #OPTIONS_PARSER.set_usage('usage: logparser.py [options]')
    (OPTIONS, ARGS) = OPTIONS_PARSER.parse_args()
    try:
        main(OPTIONS)
    except:
        OPTIONS_PARSER.print_help()
        raise
