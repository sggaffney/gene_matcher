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

__author__ = 'Stephen G. Gaffney'

package_dir = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))

from .gene_matcher import match_file, Matcher
from .update_maf import update_maf_symbols
