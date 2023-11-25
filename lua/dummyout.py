#!/usr/bin/env python
# Replace a lua function with a single return, used for skipping functions while decompiling.
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


parser = ArgumentParser(description='Replace a global lua function with a stub')
parser.add_argument('input_file', type=Path, help='Input luac file')
parser.add_argument('output_file', type=Path, help='Output luac file')
parser.add_argument('function_number', type=int, help='Number of the function to dummy out')
args = parser.parse_args()

with try_open(args.input_file, 'rb') as fi:
    lua_in = fi.read()
    luac = Luac(lua_in)

func = luac.func.funcs[args.function_number]

print(f'Skipped function #{args.function_number} has the following parameters:')
print(f'Line defined: {func.line_defined}')
print(f'Last line defined: {func.last_line_defined}')
print(f'Number of parameters: {func.number_of_parameters}')
print(f'Number of subfunctions: {len(func.funcs)}')
print(f'Local variables ({len(func.local_vars)}): {", ".join([var.name.decode("utf-8") for var in func.local_vars])}')
print(f'Upvalues ({func.number_of_upvalues}): {", ".join([var.decode("utf-8") for var in func.upvalues])}')

func.source = bytes()
func.line_defined = 0
func.last_line_defined = 0
func.number_of_upvalues = 0
func.number_of_parameters = 0
func.vararg_type = 0
func.max_stack_size = 0
func.code = [ 0x0000001E ]
func.consts = []
func.funcs = []
func.line_info = [ 1 ]
func.local_vars = []
func.upvalues = []

with try_open(args.output_file, 'wb') as fo:
    lua_out = luac.pack()
    fo.write(lua_out)