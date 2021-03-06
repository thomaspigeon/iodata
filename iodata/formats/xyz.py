# IODATA is an input and output module for quantum chemistry.
# Copyright (C) 2011-2019 The IODATA Development Team
#
# This file is part of IODATA.
#
# IODATA is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# IODATA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
# --
"""XYZ file format.

Usually, the different frames in a trajectory describe different geometries of the same
molecule, with atoms in the same order. The ``load_many`` and ``dump_many`` functions
below can also handle an XYZ with different molecules, e.g. a molecular database.
"""


from typing import TextIO, Iterator

import numpy as np

from ..docstrings import (document_load_one, document_load_many, document_dump_one,
                          document_dump_many)
from ..iodata import IOData
from ..periodic import sym2num, num2sym
from ..utils import angstrom, LineIterator


__all__ = []


PATTERNS = ['*.xyz']


@document_load_one("XYZ", ['atcoords', 'atnums', 'title'])
def load_one(lit: LineIterator) -> dict:
    """Do not edit this docstring. It will be overwritten."""
    size = int(next(lit))
    title = next(lit).strip()
    atcoords = np.empty((size, 3), float)
    atnums = np.empty(size, int)
    for i in range(size):
        words = next(lit).split()
        try:
            atnums[i] = sym2num[words[0].title()]
        except KeyError:
            atnums[i] = int(words[0])
        atcoords[i, 0] = float(words[1]) * angstrom
        atcoords[i, 1] = float(words[2]) * angstrom
        atcoords[i, 2] = float(words[3]) * angstrom
    return {
        'title': title,
        'atcoords': atcoords,
        'atnums': atnums
    }


@document_load_many("XYZ", ['atcoords', 'atnums', 'title'])
def load_many(lit: LineIterator) -> Iterator[dict]:
    """Do not edit this docstring. It will be overwritten."""
    # XYZ Trajectory files are a simple concatenation of individual XYZ files,'
    # making it travial to load many frames.
    while True:
        try:
            yield load_one(lit)
        except StopIteration:
            return


@document_dump_one("XYZ", ['atcoords', 'atnums'], ['title'])
def dump_one(f: TextIO, data: IOData):
    """Do not edit this docstring. It will be overwritten."""
    print(data.natom, file=f)
    print(data.title or 'Created with IOData', file=f)
    for i in range(data.natom):
        n = num2sym[data.atnums[i]]
        x, y, z = data.atcoords[i] / angstrom
        print(f'{n:2s} {x:15.10f} {y:15.10f} {z:15.10f}', file=f)


@document_dump_many("XYZ", ['atcoords', 'atnums'], ['title'])
def dump_many(f: TextIO, datas: Iterator[IOData]):
    """Do not edit this docstring. It will be overwritten."""
    # Similar to load_many, this is relatively easy.
    for data in datas:
        dump_one(f, data)
