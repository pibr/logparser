from optparse import OptionParser
import pandas as pd
import re


class Utils(object):

    class Settings(object):
        input_file = str()
        output_file = str()
        output_format = str()
        template = str()

    reduction_rules = {r'\[RemotePlayer\((?P<player_id>\d+)\)': r'RP\g<player_id>',
                 r'\[MediaCaptureProxy\]': r'MCP',
                 r'\[Transcoder\]': r'T',
                 r'- Using': r'U',
                 r'- Released': r'R'
                 }
    colors = []

    formats = [
        {'bg_color': 'red', 'font_color': 'black'},
        {'bg_color': 'green', 'font_color': 'black'},
        {'bg_color': 'orange', 'font_color': 'black'},
        {'bg_color': 'blue', 'font_color': 'black'}
    ]

    textToFormat = {' R': formats[2],
                    '  U': formats[1],
                    ' CR': formats[4],
                    ' CU': formats[3]

                    }
    compiled_rules = dict()

    @staticmethod
    def read_rules():
    for key in Utils.reduction_rules:
        compiled_rules[re.compile(key)] = Utils.reduction_rules[key]

    class contig_mem_regex(object):
        remote_player = re.compile(r'\[RemotePlayer\((?P<player_id>\d+)\)')
        media_capute_proxy = re.compile(r'\[MediaCaptureProxy\]')
        transcoder = re.compile(r'\[Transcoder\]')
        using = re.compile(r'- Using')
        released = re.compile('- Released')

    data_frame = None

    @staticmethod
    def __format_input():
        pass

    @staticmethod
    def to_xls():
        pass

   

    @staticmethod
    def mark_change(current, prev):
        if isinstance(current, basestring) and prev != current:
            pos = len(current) - 1
            current = current[:pos] + 'C' + current[pos:]
        return current

    @staticmethod
    def _normalise_contig_mem_entries(line):
        if isinstance(line, basestring):
            line = Utils.contig_mem_regex.remote_player.sub(
                r'RP\g<player_id>', line)
            line = Utils.contig_mem_regex.media_capute_proxy.sub("MCP", line)
            line = Utils.contig_mem_regex.transcoder.sub("T", line)
            line = Utils.contig_mem_regex.using.sub("U", line)
            line = Utils.contig_mem_regex.released.sub("R", line)
        return line


def main(options):
    """Entry point"""
    Utils.Settings.inputfile = options.input
    Utils.Settings.outputfile = options.output
    Utils.data_frame = pd.read_csv(Utils.Settings.inputfile, delimiter=';')
    Utils.data_frame = Utils.data_frame.applymap(
        Utils._normalise_contig_mem_entries)

    for column in Utils.data_frame:
        helper = column + '_shifted'
        if column != 'Timestamp' and column != 'Device':
            Utils.data_frame[helper] = Utils.data_frame[column].shift(1)
            Utils.data_frame[column] = Utils.data_frame.apply(
                lambda row: Utils.mark_change(row[column], row[helper]), axis=1)
            del Utils.data_frame[helper]
    # Utils.data_frame.style.applymap(Utils.color_red_or_green)
    writer = pd.ExcelWriter(Utils.Settings.outputfile, engine='xlsxwriter')
    Utils.data_frame.to_excel(writer, sheet_name='Results')
    # Get the xlsxwriter workbook and worksheet objects.
    workbook = writer.book
    worksheet = writer.sheets['Results']
    format_red = workbook.add_format(
        {'bg_color': 'red', 'font_color': 'black'})
    format_green = workbook.add_format(
        {'bg_color': 'green', 'font_color': 'black'})
    format_orange = workbook.add_format(
        {'bg_color': 'orange', 'font_color': 'black'})
    format_blue = workbook.add_format(
        {'bg_color': 'blue', 'font_color': 'black'})

    x = len(Utils.data_frame.columns)
    y = len(Utils.data_frame)
    worksheet.conditional_format(0, 0, y, x, {'type': 'text',
                                              'criteria': 'containing', 'value': ' R', 'format': format_green})
    worksheet.conditional_format(0, 0, y, x, {'type': 'text',
                                              'criteria': 'containing', 'value': ' U', 'format': format_red})
    worksheet.conditional_format(0, 0, y, x, {'type': 'text',
                                              'criteria': 'containing', 'value': ' CR', 'format': format_blue})
    worksheet.conditional_format(0, 0, y, x, {'type': 'text',
                                              'criteria': 'containing', 'value': ' CU', 'format': format_orange})
    writer.save()

if __name__ == "__main__":
    OPTIONS_PARSER = OptionParser()
    OPTIONS_PARSER.add_option("-i", "--input",
                              action="store", type="string", dest="input", default="input.log",
                              help="reads input to parse from CSV_FILE", metavar="CSV_FILE")
    OPTIONS_PARSER.add_option("-o", "--output",
                              action="store", type="string", dest="output", default="output.xlsx",
                              help="stores output to FILE", metavar="FILE")
    OPTIONS_PARSER.add_option("-f", "--format",
                              action="store", type="string", dest="format", default="",
                              help="formats output to desired format", metavar="FORMAT")
    OPTIONS_PARSER.add_option("-t", "--template",
                              action="store", type="string", dest="template", default="",
                              help="reads parsing rules from TEMPLATE file", metavar="TEMPLATE")
    (OPTIONS, ARGS) = OPTIONS_PARSER.parse_args()
    try:
        OPTIONS_PARSER.print_help()
        main(OPTIONS)
    except:
        OPTIONS_PARSER.print_help()
        raise
