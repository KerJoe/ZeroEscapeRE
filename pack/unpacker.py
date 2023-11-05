# Pack unpacker.
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
from pack import Pack
from helper import *
import os


parser = ArgumentParser(description='Pack file unpacker')
parser.add_argument('input_pack', type=Path, help='Zero Escape PACK resource file path')
parser.add_argument('output_directory', type=Path, help='Directory path of extraction location')
parser.add_argument('-f', '--flat', action='store_true', help='Don\'t create directories, extract every file into root')
args = parser.parse_args()


pack = Pack()
with try_open(args.input_pack, "rb") as fi:
    pack.open(fi)

    try_write_directory(args.output_directory)
    args.output_directory.mkdir(exist_ok=True)

    for file_count, file in enumerate(pack.files):
        if args.flat:
            filepath = args.output_directory/Path(file.name).name
        else:
            filepath = args.output_directory/Path(file.name)
            try_write_directory(args.output_directory)
            filepath.parent.mkdir(parents=True, exist_ok=True)

        with try_open(filepath, 'wb') as fo:
            fo.write(pack.read(fi, file))

        print (f"Extracted file {file_count+1}/{len(pack.files)}")

    # abs_file_count = 0
    # for directory_count, directory in enumerate(pack.directories):
    #     if args.flat:
    #         directory_path = args.output_directory
    #     else:
    #         directory_path = args.output_directory/f'{directory_count}-{directory.name_hash}'
    #         if not os.path.isdir(directory_path):
    #             os.mkdir(directory_path)

    #     for file_count, file in enumerate(directory.files):
    #         file_path = directory_path/f'{abs_file_count}-{file.name_hash}'
    #         with try_open(file_path, 'wb') as fo:
    #             fo.write(pack.read(fi, file))

    #         abs_file_count += 1
    #         print (f"Extracted file {file_count+1}/{len(directory.files)}, in directory {directory_count+1}/{len(pack.directories)}")
