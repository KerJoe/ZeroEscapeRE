# BinDot unpacker.
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


parser = ArgumentParser(description='BinDot file unpacker')
parser.add_argument('input_bindot', type=Path, help='Zero Escape .bin resource file path')
parser.add_argument('output_directory', type=Path, help='Directory path of extraction location')
parser.add_argument('-k', '--key', type=int, help='Decryption key, if not specified will be auto detected')
parser.add_argument('-f', '--flat', action='store_true', help='Don\'t create directories, extract every file into root')
args = parser.parse_args()


bin_dot = BinDot()
with try_open(args.input_bindot, 'rb') as fi:
    bin_dot.open(fi, args.key)

    try_write_directory(args.output_directory)
    args.output_directory.mkdir(exist_ok=True)

    abs_file_count = 0
    for directory_count, directory in enumerate(bin_dot.directories):
        if args.flat:
            directory_path = args.output_directory
        else:
            directory_path = args.output_directory/f'{directory_count}-{directory.name_hash}'
            try_write_directory(directory_path)
            directory_path.mkdir(exist_ok=True)

        for file_count, file in enumerate(directory.files):
            file_path = directory_path/f'{abs_file_count}-{file.name_hash}'
            with try_open(file_path, 'wb') as fo:
                fo.write(bin_dot.read(fi, file))

            abs_file_count += 1
            print(f'Extracted file {file_count+1}/{len(directory.files)}, in directory {directory_count+1}/{len(bin_dot.directories)}')
