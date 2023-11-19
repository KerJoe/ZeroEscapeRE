#!/usr/bin/env python
# Modify a single file in a BinDot file.
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

from pathlib import Path
from argparse import ArgumentParser
from bindot import BinDot


parser = ArgumentParser(description='BinDot file patcher')
parser.add_argument('inout_bindot', type=Path, help='Path to the BinDot file which will be operated upon')
parser.add_argument('input_patch', type=Path, help='File to be patched into the BinDot')
parser.add_argument('input_hash', type=int, help='Hashed path of the file which data will be replaced')
parser.add_argument('-s', '--size', type=int, help='Amount of space to allocate for the patched file entry, for future faster packing')
parser.add_argument('-k', '--key', type=int, help='Decryption key, if not specified auto detected')
args = parser.parse_args()


bin_dot = BinDot()
with open(args.inout_bindot, 'rb') as fi:
    bin_dot.open(fi, args.key)

file_input_size = args.input_patch.stat().st_size
file_output_size = file_input_size
if args.size:
    if args.size < file_input_size:
        print("Requested allocation size is less than the actual file size, alocation size will be set to the file size")
    else:
        file_output_size = args.size

# Assert that file offsets are monotonic
offset = -1
for file in bin_dot.files:
    assert file.offset > offset
    offset = file.offset

patch_file = None; next_file = None; next_file_count = None
for file_count, file in enumerate(bin_dot.files):
    if file.name_hash == args.input_hash:
        patch_file = file
        if file_count != len(bin_dot.files) - 1:
            next_file_count = file_count + 1
            next_file = bin_dot.files[next_file_count]
        break
if not patch_file:
    print(f'No file with hash "{args.input_hash}" was found inside the BinDot')
    exit(1)
patch_file.size = file_input_size

extra_space_needed = 0
if next_file:
    if file_output_size > next_file.offset - patch_file.offset:
        extra_space_needed = file_output_size - (next_file.offset - patch_file.offset)
        print(f'Expanding file by {extra_space_needed} bytes')
        for file_count in range(next_file_count, len(bin_dot.files)):
            bin_dot.files[file_count].offset += extra_space_needed

with open(args.inout_bindot, 'r+b') as fo:
    if extra_space_needed:
        fo.seek(bin_dot.data_pos + next_file.offset - extra_space_needed)
        data = fo.read()
        fo.seek(bin_dot.data_pos + next_file.offset)
        fo.write(data)
        fo.seek(0)
        bin_dot.save(fo, args.key)
    fo.seek(bin_dot.data_pos + file.offset)
    with open(args.input_patch, 'rb') as fi:
        bin_dot.write(fi.read(), fo, patch_file)

print(f'Wrote: {file_input_size} bytes')
if next_file:
    print(f'Padding: {next_file.offset - patch_file.offset - patch_file.size} bytes')
else:
    print('Padding: - (last file)')
