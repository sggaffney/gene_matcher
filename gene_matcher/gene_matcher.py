"""
Copyright (C) 2016 Stephen Gaffney

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
from collections import OrderedDict
import pandas as pd
from .initialize_db import build_ref_db, build_user_db
from . import package_dir

__author__ = 'Stephen G. Gaffney'


class Matcher(object):
    """Performs matching and file saving."""

    ref_file = os.path.join(package_dir, "gene_lookup_refs.db")

    def __init__(self):
        """Set up refs and user table."""
        build_ref_db(ref_file=Matcher.ref_file)
        engine, meta, refs, user = build_user_db(ref_file=Matcher.ref_file,
                                                 echo=False)
        self.engine = engine
        self.refs = refs
        self.user = user
        self.n_matched = 0
        self.n_failed = 0
        # DATAFRAMES:
        self.df_full = None
        self.df_matched = None
        self.df_failed = None

    def set_data(self, symbols=None, chromosomes=None):
        """Create 'user' db table from user_symbol and chromosome iterables."""
        if symbols is None or chromosomes is None:
            raise ValueError(
                "Symbol and chromosome iterables must be specified.")
        if len(symbols) != len(chromosomes):
            raise ValueError(
                "Symbol and chromosome iterables must be same length.")
        data = OrderedDict(user_symbol=symbols, chromosome=chromosomes)
        self.engine.execute(self.user.delete())  # make sure user table is empty
        df = pd.DataFrame(data)
        df.to_sql('user', self.engine, if_exists='append', index=False)
        self._run_matches()
        self._copy_to_dataframes()

    def import_file(self, file_path):
        df = pd.read_csv(file_path, sep='\t',
                         names=['user_symbol', 'chromosome'])
        symbols = df.user_symbol
        chromosomes = df.chromosome
        self.set_data(symbols=symbols, chromosomes=chromosomes)

    def _copy_to_dataframes(self):
        """Save 3 dataframes: full, matched, failed."""

        self.df_full = pd.read_sql(
            "select user_symbol, chromosome, case when hugo is null "
            "then user_symbol else hugo end as hugo, "
            "case when entrez_id is null then 0 else entrez_id end "
            "as entrez_id from user order by id asc;",
            self.engine, coerce_float=False)

        self.df_matched = pd.read_sql(
            "select * from user where hugo is not null order by id;",
            self.engine, coerce_float=False)
        self.n_matched = len(self.df_matched)

        self.df_failed = pd.read_sql("select * from user where hugo is null;",
                                     self.engine, coerce_float=False)
        self.n_failed = len(self.df_failed)

    @staticmethod
    def _update_matches(conditions):
        """Uses matching conditions to build SQL statement, mapping refs->user.
        Args:
            conditions (iterable of strings): matching statement(s), specifying
                'user.' before user fields. other fields are
                from refs table. used for correlated subqueries.
                e.g. ['user.user_symbol = hugo', 'user.chromosome = chromosome']
        Returns:
            SQL string for updating User table.
        """
        if conditions is None:
            raise ValueError("Conditions required.")
        condition = ' AND '.join(conditions)
        # GENERIC MATCHING STATEMENT, VARIES WITH CONDITION
        cmd = """UPDATE user
            SET hugo=(SELECT hugo FROM refdb.refs WHERE {condition}),
            entrez_id=(SELECT geneId FROM refdb.refs WHERE {condition})
            WHERE hugo is null
            and EXISTS (SELECT 1 FROM refdb.refs WHERE {condition});"""
        s = cmd.format(condition=condition)
        return s

    @staticmethod
    def _cal_fix(hugo, entrez, user_symbol, chromosome):
        return """update user set hugo = {hugo!r}, entrez_id = {entrez}
            where hugo is null and user_symbol = {user_sym!r}
            and chromosome = {chrom!r};""".\
            format(hugo=hugo, entrez=entrez, user_sym=user_symbol,
                   chrom=chromosome)

    def _run_matches(self):
        """Execute pre-defined series of SQL commands."""
        m_hugo = "user.user_symbol = hugo"
        m_chr = "user.chromosome = chromosome"
        m_synonym = "'|' || synonyms || '|' LIKE '%|' " \
                    "|| user.user_symbol || '|%'"
        m_chr_amb = "chromosome like '%|%' AND '|' || chromosome || '|' " \
                    "LIKE '%|' || user.chromosome || '|%'"
        m_type = "type_of_gene not in ('pseudo', 'unknown', 'other')"

        statements = [
            self._update_matches([m_hugo, m_chr]),
            self._update_matches([m_synonym, m_chr]),
            self._update_matches([m_hugo, m_chr_amb]),
            self._update_matches([m_synonym, m_chr_amb]),
            self._update_matches([m_synonym, m_chr, m_type]),
            self._update_matches([m_synonym, m_chr_amb, m_type]),
        ]

        calendar_map = [('DEC1', 50514, '1-Dec', '9'),
                        ('FEB1', 2233, '1-Feb', '8'),
                        ('FEB10', 100271923, '10-Feb', '3'),
                        ('FEB2', 2234, '2-Feb', '19'),
                        ('FEB5', 619398, '5-Feb', '6'),
                        ('FEB6', 619397, '6-Feb', '18'),
                        ('FEB7', 100049160, '7-Feb', '21'),
                        ('FEB9', 100188849, '9-Feb', '3'),
                        ('MARCH1', 55016, '1-Mar', '4'),
                        ('MARC1', 64757, '1-Mar', '1'),
                        ('MARCH10', 162333, '10-Mar', '17'),
                        ('MARCH11', 441061, '11-Mar', '5'),
                        ('MARCH2', 51257, '2-Mar', '19'),
                        ('MARC2', 54996, '2-Mar', '1'),
                        ('MARCH3', 115123, '3-Mar', '5'),
                        ('MARCH4', 57574, '4-Mar', '2'),
                        ('MARCH5', 54708, '5-Mar', '10'),
                        ('MARCH6', 10299, '6-Mar', '5'),
                        ('MARCH7', 64844, '7-Mar', '2'),
                        ('MARCH8', 220972, '8-Mar', '10'),
                        ('MARCH9', 92979, '9-Mar', '12'),
                        ('SEPT1', 1731, '1-Sep', '16'),
                        ('SEPT10', 151011, '10-Sep', '2'),
                        ('SEPT11', 55752, '11-Sep', '4'),
                        ('SEPT12', 124404, '12-Sep', '16'),
                        ('SEPT14', 346288, '14-Sep', '7'),
                        ('SEPT2', 4735, '2-Sep', '2'),
                        ('SEPT3', 55964, '3-Sep', '22'),
                        ('SEPT4', 5414, '4-Sep', '17'),
                        ('SEPT5', 5413, '5-Sep', '22'),
                        ('SEPT6', 23157, '6-Sep', 'X'),
                        ('SEPT7', 989, '7-Sep', '7'),
                        ('SEPT8', 23176, '8-Sep', '5'),
                        ('SEPT9', 10801, '9-Sep', '17')]
        cal_cmds = [self._cal_fix(*i) for i in calendar_map]

        with self.engine.begin() as conn:
            for s in statements + cal_cmds:
                conn.execute(s)

    def export_matches(self, basename):
        """Save results to success + failure files."""
        full_path = basename + '_full.txt'
        good_path = basename + '_converted.txt'
        fail_path = basename + '_failed.txt'

        # all rows
        self.df_full.to_csv(full_path, sep='\t', index=False)

        # successful rows
        self.df_matched[self.df_matched.columns.drop('id')].\
            to_csv(good_path, sep='\t', index=False)

        # failed rows
        if len(self.df_failed):
            self.df_failed[['user_symbol', 'chromosome']].\
                to_csv(fail_path, sep='\t', index=False, header=False)


def match_file(user_path=None, matcher=None):
    """Perform matching on specified file. Optionally provide matcher object."""
    if not user_path:
        raise ValueError("Specify input data file.")
    matcher = Matcher() if not matcher else matcher
    matcher.import_file(user_path)
    file_root = os.path.basename(user_path)
    matcher.export_matches(file_root)
    print("{} matches, {} unmatched.".format(
        matcher.n_matched, matcher.n_failed
    ))
    return matcher
