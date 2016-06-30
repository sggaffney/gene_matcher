__author__ = 'Stephen G. Gaffney'

from setuptools import setup

setup(name='gene_matcher',
      version='0.1',
      description='Fetch HUGO symbol and entrez id from symbol and chromosome.',
      url='http://github.com/sggaffney',
      author='Stephen G. Gaffney',
      author_email='stephen.gaffney@yale.edu',
      license='GPLv3',
      packages=['gene_matcher'],
      install_requires=[
          'pandas', 'sqlalchemy'
      ],
      scripts=['bin/gene_matcher', 'bin/update_maf'],
      zip_safe=False,
      data_files=[('gene_matcher', ['gene_matcher/gene_lookup_refs.db'])])
