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
import re

import pandas as pd

from . import Matcher

__author__ = 'Stephen G. Gaffney'

m = Matcher()


def update_maf_symbols(maf_path, out_path=None, drop_unmatched=False):
    """Create new MAF file with updated Hugo_Symbol and Entrez_Gene_Id columns.

    Matching is based on symbol and chromosome only. Failed matches maintain
    original symbol and set Entrez_Gene_Id to 0.

    Args:
        drop_unmatched (bool): drop lines that fail to match.
        out_path (str): optional path for new MAF file. Default is current path
            with extension removed and suffix '_hugofix.maf'

    Returns:
        out_path (str): path to new MAF file.
    """
    if not out_path:
        out_path = os.path.splitext(maf_path)[0] + '_hugofix.maf'

    df = pd.read_csv(maf_path, sep='\t', comment='#', usecols=pd.np.arange(19))

    # Ensure correct column names
    hugo_col = [i for i in df if re.search(r'\bhugo', i.lower())][0]
    chr_col = [i for i in df if re.search(r'\bchr', i.lower())][0]
    entrez_col = [i for i in df if re.search(r'\bentrez', i.lower())][0]
    pos_start_col = [i for i in df if re.search(r'\bstart_pos', i.lower())][0]
    pos_end_col = [i for i in df if re.search(r'\bend_pos', i.lower())][0]
    df.rename(columns={hugo_col: 'Hugo_Symbol', entrez_col: 'Entrez_Gene_Id',
                       chr_col: 'Chromosome', pos_start_col: 'Start_Position',
                       pos_end_col: 'End_Position'}, inplace=True)

    genes = df[['Hugo_Symbol', 'Chromosome']].drop_duplicates()
    m.set_data(genes.Hugo_Symbol, genes.Chromosome)
    full = pd.merge(df, m.df_matched, how='left',
                    left_on=['Hugo_Symbol', 'Chromosome'],
                    right_on=['user_symbol', 'chromosome'])

    full.hugo = full.hugo.fillna(full.Hugo_Symbol)
    full.entrez_id = full.entrez_id.fillna(0)
    df['Hugo_Symbol'] = full.hugo
    df['Entrez_Gene_Id'] = full.entrez_id

    if drop_unmatched:
        df.dropna(subset=['Hugo_Symbol'], inplace=True)
    df.Entrez_Gene_Id = df.Entrez_Gene_Id.astype(int)
    df.to_csv(out_path, sep='\t', index=False)
    return out_path
