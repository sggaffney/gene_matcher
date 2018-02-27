# gene_matcher

<!-- MarkdownTOC -->

- [Usage](#usage)
    - [Input](#input)
    - [Output](#output)
- [Installation](#installation)
- [Gene database update](#gene-database-update)
- [License](#license)

<!-- /MarkdownTOC -->


Looks up **HUGO symbols** and **Entrez IDs** from gene symbol–chromosome pairs
for human genes.

* Updates out-of-date symbols.

    ```
    MLL2, chr19 -> KMT2D, entrez 8085
    MLL4, chr12 -> KMT2B, entrez 9757
    ```

* Fixes Excel-mangling of the 34 gene symbol that are converted into dates.
    ```
    1-Dec, chr9 -> DEC1, entrez 50514
    1-Feb, chr8 -> FEB1, entrez 2233
    2-Feb, chr19 -> FEB2, entrez 2234
    ```

Matching is performed using symbols and synonym lists from the NCBI Gene database, using the reference file [Homo_sapiens.gene_info.gz][1]. The synonym list from this reference should be adequate for matching the vast majority of uncommon or out of date symbols, but will fail to match some LOCXXX genes and FLJXXX symbols.


Usage
-----

```
$ gene_matcher /path/to/input_file.txt
```

#### Input

Example tab-delimited input file, *test_genes.txt*:
```
MLL4	12
MLL2	19
TP53	17
ABC2	9
SPRY3	X
1-Dec	9
1-Mar	4
MTCYB	MT
FLJ43860	8
LOC100509575	X
```
* Valid chromosomes are 1-22,X,Y,MT

#### Output

Three tab-delimited text files are produced:

* *Full* results set, with one row for each input row.

    ```
    user_symbol     chromosome  hugo            entrez_id
    MLL4            12          KMT2D           8085
    MLL2            19          KMT2B           9757
    TP53            17          TP53            7157
    ABC2            9           ABCA2           20
    SPRY3           X           SPRY3           10251
    1-Dec           9           DEC1            50514
    1-Mar           4           MARCH1          55016
    MTCYB           MT          MT-CYB          4519
    FLJ43860        8           FLJ43860        0
    LOC100509575    X           LOC100509575    0
    ```
    * For failed matches, the input symbol is repeated in the `hugo` column and
      `entrez_id` is set to 0.
    * Including every row allows horizontal concatenation with the source of the
      input file, using Excel or a unix tool such as `paste`.

* The partial *converted* set, containing the lines from the *full* set with matches.
* The *failed* input lines.


Installation
------------

Install the package into your local python distribution by running the following
in the command line:
```
pip install git+https://github.com/sggaffney/gene_matcher.git
```

This will place the script `gene_matcher` on your path.


Gene database update
---------------

To update the reference gene set to the latest version from NCBI Gene database, export the following columns from the [reference file][1] into a new tab-separated text file (`genes.txt`): `geneId`, `symbol`, `chromosome`, `Synonyms`, `type_of_gene`.

*Note*: If you have a MySQL database reflecting the current table, you can export as follows:
```sql
select 'geneId', 'symbol', 'chromosome', 'Synonyms', 'type_of_gene'
union all
select `geneId`, `symbol`, `chromosome`, `Synonyms`, `type_of_gene` from ncbi_entrez where `Symbol_from_nomenclature_authority` <> '-'
into outfile '/tmp/genes.txt';
```

Use this file to overwrite the `genes.txt` file in your `gene_matcher.__path__` directory, and delete the current `gene_lookup_refs.db` file in the same directory. This database file will be rebuilt when you next import the package:

```
python -c "import gene_matcher"`
```

License
-------

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


[1]: ftp://ftp.ncbi.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz "Homo_sapiens.gene_info.gz"

