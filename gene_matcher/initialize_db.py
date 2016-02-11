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
__author__ = 'Stephen G. Gaffney'

import os
import pandas as pd
from sqlalchemy import Table, Column, Integer, String, Index, MetaData, \
    create_engine
from . import package_dir


def build_ref_db(ref_file=None):
    """Create refs table (ncbi_entrez) in sqlite file if doesn't exist."""
    if ref_file is None:
        raise ValueError("ref_file sqlite path must be specified.")
    ref_engine = create_engine('sqlite:///' + ref_file)  # sqlite
    # POPULATE IF EMPTY
    if not ref_engine.has_table('refs'):
        metaref = MetaData()
        refs = Table('refs', metaref,
                     Column('geneId', Integer, primary_key=True),
                     Column('hugo', String(255)),
                     Column('chromosome', String(255)),
                     Column('synonyms', String(255)),
                     Column('type_of_gene', String(255)),
                     Index('refs_hugo_chrom', 'hugo', 'chromosome', unique=True)
                     )
        metaref.create_all(ref_engine, tables=[refs])  # create if not present
        df = pd.read_csv(os.path.join(package_dir, 'genes.txt'), sep='\t',
                         names=['geneId', 'hugo', 'chromosome',
                                'synonyms', 'type_of_gene'])
        df.to_sql('refs', ref_engine, if_exists='append', index=False)


def build_user_db(ref_file=None, echo=False):
    """Initialize user db file.

    Returns:
        engine: db engine,
        meta: MetaData object,
        user: user table,
        refs: refs table.
    """
    if ref_file is None:
        raise ValueError(
            "ref_file and user_file sqlite paths must be specified.")
    # USER DATABASE FILE
    engine = create_engine('sqlite://', echo=echo)  # in memory
    engine.execute("attach database '{ref_file}' as refdb;".
                   format(ref_file=ref_file))  # attach. auto-closed.

    # DEFINE TABLES
    meta = MetaData()
    refs = Table('refs', meta,
                 Column('geneId', Integer, primary_key=True),
                 Column('hugo', String(255)),
                 Column('chromosome', String(255)),
                 Column('synonyms', String(255)),
                 Column('type_of_gene', String(255)),
                 Index('refs_hugo_chrom', 'hugo', 'chromosome', unique=True),
                 schema='refdb')
    user = Table('user', meta,
                 Column('id', Integer, primary_key=True),
                 Column('user_symbol', String(255)),
                 Column('chromosome', String(255), nullable=True),
                 Column('hugo', String(255), nullable=True),
                 Column('entrez_id', Integer, nullable=True))

    # INITIALIZE LOOKUP.DB / USER TABLE, deleting if extant
    if engine.has_table('user'):
        user.drop(engine)
    meta.create_all(engine, tables=[user])
    return engine, meta, refs, user


def import_user_list(user_path=None, engine=None):
    if not user_path or not engine:
        raise ValueError("Both user_path and engine must be specified.")
    df = pd.read_csv(user_path, sep='\t', names=['user_symbol', 'chromosome'])
    df.to_sql('user', engine, if_exists='append', index=False)
    return user_path
