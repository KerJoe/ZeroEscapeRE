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
import os


parser = ArgumentParser(description='Zero Escape data file patcher')
parser.add_argument('filename_data', type=Path, help='Input data file path, for copying the main structure from')
parser.add_argument('filename_patch', type=Path, help='File to be patched')
parser.add_argument('hash_patch', type=int, help='Path hash of the patch file')
parser.add_argument('-s', '--size', type=int, help='Amount of space to allocate for patched file entry, for faster packing')
parser.add_argument('-k', '--key', type=int, help='Decryption key, if not specified auto detected')
args = parser.parse_args()


if not os.path.isfile(args.filename_data):
    print("Input file does not exist or is a folder.")
    exit(1)

if not os.path.isfile(args.filename_patch):
    print("Patch file does not exist or is a folder.")
    exit(2)


bin_dot = BinDot()
with open(args.filename_data, "rb") as fi:
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

print(f"Entry size: {patch_file_entry.size} bytes")
prev_size = patch_file_entry.size
patch_file_entry.size = os.path.getsize(args.filename_patch)
patch_file_entry.padding = prev_size - patch_file_entry.size
with open (args.filename_data, "r+b") as fo:
    bin_dot.save(fo)

    with open (args.filename_patch, "rb") as fpi:
        bin_dot.write(fpi.read(), fo, patch_file_entry)
print(f"Done. Wrote: {os.path.getsize(args.filename_patch)} bytes.")