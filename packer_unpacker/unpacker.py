# Zero Escape Binary File unpacker.
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


parser = ArgumentParser(description='Zero Escape data file extractor')
parser.add_argument('filename', type=Path, help='Data file path')
parser.add_argument('folder', type=Path, help='File extraction location')
parser.add_argument('-k', '--key', type=int, help='Decryption key, if not specified auto detected')
parser.add_argument('-f', '--flat', action='store_true', help='Don\'t create folders, extract every file into root')
args = parser.parse_args()


if not os.path.isfile(args.filename):
    print("Input file does not exists, or is a folder.")
    exit(1)

if not os.path.isdir(args.folder):
    print("Output folder does not exists, or is a file.")
    exit(2)


bin_dot = BinDot()
with open(args.filename, "rb") as fi:
    bin_dot.open(fi, args.key)

    abs_file_count = 0
    for directory_count, directory_entry in enumerate(bin_dot.directories):
        directory_path = args.folder/f'{directory_count}-{directory_entry.name_hash}'

        if not args.flat and os.path.isdir(args.folder):
            os.mkdir(directory_path)

        for file_count, file_entry in enumerate(directory_entry.files):
            file_path = (args.folder if args.flat else directory_path)/f'{abs_file_count}-{file_entry.name_hash}'
            with open(file_path, 'wb') as fo:
                fo.write(bin_dot.read(fi, file_entry))

            abs_file_count += 1
            print (f"Extracted file {file_count+1}/{len(directory_entry.files)}, in folder {directory_count+1}/{len(bin_dot.directories)}")
