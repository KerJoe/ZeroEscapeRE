# Convert Regular lua bytecode into VLR lua bytecode
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
from luac import Luac
from helper import *


parser = ArgumentParser(description='Convert normal lua bytecode to VLR bytecode')
parser.add_argument('input_file', type=Path, help='Normal compiled lua file')
parser.add_argument('output_file', type=Path, help='VLR compiled lua file')
args = parser.parse_args()

with try_open(args.input_file, 'rb') as fi:
    lua_in = fi.read()
    luac = Luac(lua_in)

    # Do the reverse of what was done in vlr2luac.py by incrementing the opcodes after the insertion point by 2
    def traverse(func: Luac.Function):
        for code_count in range(len(func.code)):
            opc = func.code[code_count] & 0x3F
            if opc > 0x16:
                if opc > 0x25:
                    raise Exception(f'Unknown opcode: {opc}')
                func.code[code_count] += 2
        for subfunc in func.funcs:
            traverse(subfunc)
    traverse(luac.func)

    lua_out = luac.pack()
    with try_open(args.output_file, 'wb') as fo:
        fo.write(lua_out)