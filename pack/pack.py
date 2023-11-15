# Pack (Zero Escape archive format) data class.
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

from helper import *
from io import IOBase
from typing import Callable

c_decompress = import_pyx('c_decompress.pyx', __file__) # Faster Cython implementation

class Pack:
    def py_decompress(input_data: bytes) -> bytes:
        data = AccUnpack(input_data)

        uncompressed_size = data.unpack('I')
        output_data = bytearray(uncompressed_size)
        output_position = 0

        while(True):
            copy_length = data.unpack('B')

            if copy_length < 0x20: # Just copy bytes from input to output
                output_data[output_position:output_position+copy_length+1] = data.unpack(f'{copy_length+1}s')
                output_position += copy_length + 1
            else: # Clone part of previously copied data back into the output buffer
                backtrack_amount_high = copy_length & 0x1F
                copy_length = copy_length >> 5

                if (copy_length == 7): # Need to copy even more data
                    copy_length += data.unpack('B')

                backtrack_amount_low = data.unpack('B')
                backtrack_position = output_position - backtrack_amount_high * 256 - backtrack_amount_low - 1;

                for count in range(copy_length + 2): # Can overlap
                    output_data[output_position + count] = output_data[backtrack_position + count]
                output_position += copy_length + 2

            if (data.offset >= len(input_data)):
                return bytes(output_data)
    decompress = py_decompress if not c_decompress else c_decompress.decompress

    class FileEntry:
        size: int
        is_compressed: bool
        name: str

        absolute_position: int

        def __init__(self, data: AccUnpack, absolute_position: int):
            self.size = data.unpack('I')

            self.is_compressed = data.unpack('B')
            assert self.is_compressed < 2

            name_size = data.unpack('B')
            self.name = data.unpack(f'{name_size}s').decode('ascii')

            self.absolute_position = absolute_position


    files: list[FileEntry]


    def open(self, pack_file: IOBase):
        header = AccUnpack(pack_file.read(12))

        if header.unpack('4s') != b'PACK':
            raise Exception('Unknown PACK file detected')

        data_offset = header.unpack('I')
        entry_count = header.unpack('I')

        file_entries = AccUnpack(pack_file.read(data_offset - 12))
        self.files = []
        for _ in range(entry_count):
            file_entry = Pack.FileEntry(file_entries, data_offset)
            data_offset += file_entry.size
            self.files += [ file_entry ]


    def read(self, pack_file: IOBase, file_entry: FileEntry) -> bytes:
        pack_file.seek(file_entry.absolute_position)
        if file_entry.is_compressed:
            return Pack.decompress(pack_file.read(file_entry.size))
        else:
            return pack_file.read(file_entry.size)