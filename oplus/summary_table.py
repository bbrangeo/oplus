"""
Summary table
---------------


"""

import os
import re
import io

import pandas as pd

from oplus.configuration import CONF


class SummaryTableError(Exception):
    pass


class SummaryTable:
    def __init__(self, path, encoding=None):
        assert os.path.isfile(path), "No file at given path: '%s'." % path
        self.path = path
        self.encoding = CONF.encoding if encoding is None else encoding

        self.sep = None
        self.report_tables_ref = {}

        self._parse()

    def _parse(self):
        with open(self.path, encoding=self.encoding) as f:
            start_parse = False
            search_end = False
            for var in enumerate(f):
                line_nb = var[0]
                line_s = var[1]

                if 'Tabular Output Report in Format' in line_s:
                    self.sep = line_s.split(':')[1][1]

                if 'REPORT:' in line_s:
                    start_parse = True
                    if search_end:
                        self.report_tables_ref['{r}_{f}'.format(r=report, f=for_)][table_name]['lineend'] = line_nb-1
                        search_end = False
                    report = re.findall('([^%s]+)' % self.sep, line_s)[1].replace('\n', '')
                elif not start_parse:
                    continue
                elif 'FOR:' in line_s:
                    for_ = re.findall('([^%s]+)' % self.sep, line_s)[1].replace('\n', '')
                    self.report_tables_ref['{r}_{f}'.format(r=report, f=for_)] = {}
                    self.report_tables_ref['{r}_{f}'.format(r=report, f=for_)]['TableListName'] = []
                    continue

                elif not any(
                        [v in line_s for v in
                         ['Values gathered over',
                          'WARNING:',
                          'Note',
                          '----',
                          'Values in table are in hours.'
                          ]]) and line_s[0] != '%s' % self.sep and line_s[0:2] != '\n':
                    if search_end:
                        self.report_tables_ref['{r}_{f}'.format(r=report, f=for_)][table_name]['lineend'] = line_nb-1
                        search_end = False
                    table_name = line_s.split('%s' % self.sep)[0].replace('\n', '')
                    if table_name not in self.report_tables_ref['{r}_{f}'.format(r=report, f=for_)]['TableListName']:
                        self.report_tables_ref['{r}_{f}'.format(r=report, f=for_)]['TableListName'].append(table_name)
                    self.report_tables_ref['{r}_{f}'.format(r=report, f=for_)][table_name] = {}

                elif (
                    (line_s.split('%s' % self.sep)[0] == '') and
                    (line_s.split('%s' % self.sep)[1] == '') and
                    (line_s.split('%s' % self.sep)[2] != '') and
                    ('linestart' not in self.report_tables_ref['{r}_{f}'.format(
                        r=report, f=for_)][table_name].keys())
                ):
                    self.report_tables_ref['{r}_{f}'.format(r=report, f=for_)][table_name]['linestart'] = line_nb
                    search_end = True

        # TODO: Manage key error correctly
        delete_t = []
        for report_key in self.report_tables_ref.keys():
            for table_key in self.report_tables_ref[report_key].keys():
                if table_key == 'TableListName':
                    continue
                if 'linestart' not in self.report_tables_ref[report_key][table_key].keys():
                    delete_t.append((report_key, table_key))
        # remove table ref
        for (r_key, t_key) in delete_t:
            del self.report_tables_ref[r_key][t_key]
            self.report_tables_ref[r_key]['TableListName'].remove(t_key)

    def get_report_keys(self):
        return list(self.report_tables_ref.keys())

    def get_table_report_list(self, report_key):
        return self.report_tables_ref[report_key]['TableListName']

    def get_table_df(self, report_key, table_report):
        content_bytes = open(self.path, "rb").read()
        content = content_bytes.decode(self.encoding).encode('ascii', 'ignore')
        f = io.BytesIO(content)

        begin_line = self.report_tables_ref[report_key][table_report]['linestart']
        end_line = self.report_tables_ref[report_key][table_report]['lineend']

        df = pd.read_csv(
            f,
            #sep=self.sep,
            sep=None,
            skiprows=begin_line,
            nrows=end_line-begin_line-3,
            index_col=1
            )
        df = df.dropna(axis='columns', how='all')
        df = df.dropna(axis='rows', how='all')

        # delete index name
        df.index.name = None

        return df

if __name__ == '__main__':
    import oplus as op
    rsc_path = os.path.join(os.getcwd().split('oplus')[0], 'antoine-work', 'csv')

    summary = SummaryTable(os.path.join(rsc_path, 'eplustbl.csv'))
    # for k in summary.get_report_keys():
    #     if 'Sizing' in k:
    #         print(k)

    # for tablename in summary.get_table_report_list('Component Sizing Summary_Entire Facility'):
    #     print(tablename)

    # for tablename in summary.get_table_report_list('Component Sizing Summary_Entire Facility'):
    #     print(tablename)
    #     df = summary.get_table_df('Component Sizing Summary_Entire Facility', tablename)

    #
    # with open(os.path.join(rsc_path, 'eplustbl.csv'), encoding=CONF.encoding) as f:
    #     for var in enumerate(f):
    #         if var[0] > 8735 and var[0] <= 9091:
    #             print(var[1])

    df = summary.get_table_df('Component Sizing Summary_Entire Facility', 'AirTerminal:SingleDuct:Uncontrolled')
    print(df)