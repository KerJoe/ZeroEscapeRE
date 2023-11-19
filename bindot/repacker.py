#!/usr/bin/env python
# Replace all file data in BinDot file.
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
from helper import *


parser = ArgumentParser(description='BinDot file repacker')
parser.add_argument('input_bindot', type=Path, help='Source BinDot file path from which the file structure will be copied to the output file')
parser.add_argument('input_directory', type=Path, help='Directory path containing modified files extracted from BinDot')
parser.add_argument('output_bindot', type=Path, help='Path to the resulting BinDot file')
parser.add_argument('-k', '--key', type=int, help='Decryption key, if not specified will be auto detected')
parser.add_argument('-f', '--flat', action='store_true', help='Pass this flag if unpacker was called with it')
args = parser.parse_args()


bindot = BinDot()
with try_open(args.input_bindot, 'rb') as fi:
    bindot.open(fi, args.key)

with try_open(args.output_bindot, 'wb') as fo:
    abs_file_count = 0
    offset_count = 0
    file_path_list = []
    file_entry_list = []

    for directory_count, directory in enumerate(bindot.directories):
        if args.flat:
            directory_path = args.input_directory
        else:
            directory_path = args.input_directory/f'{directory_count}-{directory.name_hash}'

        for file_count, file in enumerate(directory.files):
            file_path = directory_path/f'{abs_file_count}-{file.name_hash}'
            abs_file_count += 1

            file.size = file_path.stat().st_size
            file.offset = offset_count
            offset_count += file.size

            file_path_list += [ file_path ]
            file_entry_list += [ file ]

    bindot.save(fo)
    for file_count, file_path, file in zip(range(len(file_path_list)), file_path_list, file_entry_list):
        with try_open(file_path, 'rb') as fd:
            bindot.write(fd.read(), fo, file)
        print(f'Repacked file {file_count+1}/{len(file_path_list)}')