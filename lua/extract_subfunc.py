#!/usr/bin/env python
# Make a subfunction into a main function, used for decompiling subfunctions of dummied out functions.
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


parser = ArgumentParser(description='Replace a main lua function with a sub function')
parser.add_argument('input_file', type=Path, help='Input luac file')
parser.add_argument('output_file', type=Path, help='Output luac file')
parser.add_argument('function_number', type=str, help='Dot separated number of the subfunction to extract (e.g 5.1.2.5)')
args = parser.parse_args()

function_number_list = args.function_number.split('.')
with try_open(args.input_file, 'rb') as fi:
    lua_in = fi.read()
    luac = Luac(lua_in)

func = luac.func
for function_number in function_number_list:
    func = func.funcs[int(function_number)]

luac.func = func

with try_open(args.output_file, 'wb') as fo:
    lua_out = luac.pack()
    fo.write(lua_out)