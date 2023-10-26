# Zero Escape BinDot repacker.
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
import os


parser = ArgumentParser(description='Zero Escape data file repacker')
parser.add_argument('filename_in', type=Path, help='Input data file path, for copying the main structure from')
parser.add_argument('folder', type=Path, help='File import location')
parser.add_argument('filename_out', type=Path, help='Ouput data file path, final patched file')
parser.add_argument('-k', '--key', type=int, help='Decryption key, if not specified auto detected')
parser.add_argument('-f', '--flat', action='store_true', help='Import folder data structure')
args = parser.parse_args()


if not os.path.isfile(args.filename_in):
    print("Input file does not exist or is a folder.")
    exit(1)

if not os.path.isdir(args.folder):
    print("Output folder does not exist or is a file.")
    exit(2)

if os.path.isdir(args.filename_out):
    print("Output file is a folder.")
    exit(3)


bin_dot = BinDot()
with open(args.filename_in, "rb") as fi:
    bin_dot.open(fi, args.key)

with open (args.filename_out, "wb") as fo:
    abs_file_count = 0
    offset_count = 0
    file_path_list = []
    file_entry_list = []
    for directory_count, directory_entry in enumerate(bin_dot.directories):
        directory_path = args.folder/f'{directory_count}-{directory_entry.name_hash}'

        for file_count, file_entry in enumerate(directory_entry.files):
            file_path = (args.folder if args.flat else directory_path)/f'{abs_file_count}-{file_entry.name_hash}'
            abs_file_count += 1

            file_entry.size = os.path.getsize(file_path)
            file_entry.offset = offset_count
            offset_count += file_entry.size

            file_path_list += [ file_path ]
            file_entry_list += [ file_entry ]

    bin_dot.save(fo)
    for file_count, file_path, file_entry in zip(range(len(file_path_list)), file_path_list, file_entry_list):
        with open(file_path, 'rb') as fd:
            bin_dot.write(fd.read(), fo, file_entry)
        print (f"Packed file {file_count+1}/{len(file_path_list)}")