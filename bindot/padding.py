# Add padding to a file in a BinDot file.
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


parser = ArgumentParser(description='Zero Escape data file padding adder')
parser.add_argument('filename_in', type=Path, help='Input data file path, for copying the main structure from')
parser.add_argument('filename_out', type=Path, help='Ouput data file path, final patched file')
parser.add_argument('hash_patch', type=Path, help='Path hash of the patch file')
parser.add_argument('-s', '--size', type=int, help='Amount of space to allocate for patched file entry, for faster packing')
parser.add_argument('-k', '--key', type=int, help='Decryption key, if not specified auto detected')
args = parser.parse_args()


if not os.path.isfile(args.filename_in):
    print("Input file does not exist or is a folder.")
    exit(1)

if os.path.isdir(args.filename_out):
    print("Output file is a folder.")
    exit(3)


bin_dot = BinDot()

with open(args.filename_in, "rb") as fi:
    bin_dot.open(fi, args.key)

    patch_file_entry = None
    for directory_entry in bin_dot.directories:
        for file_entry in directory_entry.files:
            if file_entry.name_hash == args.hash_patch:
                patch_file_entry = file_entry
                break
        else:
            continue
        break
    if not patch_file_entry:
        print("Patch hash was not found in data file.")
        exit(4)

    real_size = patch_file_entry.size
    patch_file_entry.size = args.size
    with open (args.filename_out, "wb") as fo:
        bin_dot.save(fo)
        patch_file_entry.size = real_size
        for directory_entry in bin_dot.directories:
            for file_entry in directory_entry.files:
                bin_dot.write(bin_dot.read(fi, file_entry), fo, file_entry)