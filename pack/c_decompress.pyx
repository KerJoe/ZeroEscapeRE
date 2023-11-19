# CPython implementation of PACK decompresssion routine.
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

from cpython.bytes cimport PyBytes_AsString, PyBytes_Size, PyBytes_FromStringAndSize

from libc.stdlib cimport free, malloc
from libc.string cimport memcpy
from libc.stdint cimport uint32_t, uint8_t


cpdef decompress(bytes input_data_bytes):
    cdef int uncompressed_size, compressed_size
    cdef int input_position, output_position, copy_length
    cdef int backtrack_amount_high, backtrack_amount_low, backtrack_position
    cdef bytes output_data_bytes

    cdef uint8_t* input_data
    cdef uint8_t* output_data

    compressed_size = PyBytes_Size(input_data_bytes)
    input_data = <uint8_t*>PyBytes_AsString(input_data_bytes)
    uncompressed_size = (<uint32_t*>input_data)[0] # Dereference 4 bytes
    output_data = <uint8_t*>malloc(uncompressed_size)
    input_position = 4
    output_position = 0

    while(input_position < compressed_size):
        copy_length = input_data[input_position]; input_position += 1

        if copy_length < 0x20: # Just copy bytes from input to output
            memcpy(output_data + output_position, input_data + input_position, copy_length + 1)
            input_position += copy_length + 1; output_position += copy_length + 1
        else: # Clone part of previously copied data back into output buffer
            backtrack_amount_high = copy_length & 0x1F
            copy_length >>= 5

            if copy_length == 7: # Need to copy even more data
                copy_length += input_data[input_position]; input_position += 1

            backtrack_amount_low = input_data[input_position]; input_position += 1
            backtrack_position = output_position - ((backtrack_amount_high << 8) | backtrack_amount_low) - 1

            if backtrack_position + copy_length + 2 >= output_position: # Check if memory overlaps
                for count in range(copy_length + 2):
                    output_data[output_position + count] = output_data[backtrack_position + count]
            else: # Use memcpy if memory is not overlapping
                memcpy(output_data + output_position, output_data + backtrack_position, copy_length + 2)
            output_position += copy_length + 2

    output_data_bytes = PyBytes_FromStringAndSize(<char*>output_data, uncompressed_size)
    free(output_data)
    return output_data_bytes