# Various utility functions.
# Copyright (C) 2023 KerJoe.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import struct
from typing import Generator

def div_to_chunks(L: list, n: int) -> Generator[list, None, None]:
    """ Yield successive n-sized chunks from L """
    for i in range(0, len(L), n):
        yield L[i:i+n]

class AccUnpack:
    offset: int
    data: bytes
    byte_order: str

    def __init__(self, data: bytes, offset: int=0, byte_order: str="<"):
        self.offset = offset
        self.data = data
        self.byte_order = byte_order

    def unpack(self, format: str) -> tuple | object:
        """ Unpack data using 'format' and increment position """
        output = struct.unpack_from(self.byte_order+format, self.data, self.offset)
        self.offset += struct.calcsize(self.byte_order+format)
        return output[0] if len(output) == 1 else output

    def unpack_list(self, format: str, amount: int, data_class: object=None) -> list:
        """ Unpack uniform 'amount' of data using 'format' into a list of tuples, or  a list of 'data_class' """
        output = []
        for _ in range(amount):
            if data_class:
                output += [ data_class(self.unpack(format)) ]
            else:
                output += [ self.unpack(format) ]
        return output
