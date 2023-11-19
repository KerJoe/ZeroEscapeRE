# Compiled lua dataclass
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

from helper import *
import itertools
import struct


class Luac:
    class Header:
        magic: bytes
        version: int
        is_little_endian: bool
        format_version: int
        size_of_int: int
        size_of_size_t: int
        size_of_instr: int
        size_of_number: int
        is_integral_float: bool

        def __init__(self, data: list):
            self.magic = data[0]
            self.version = data[1]
            self.format_version = data[2]
            self.is_little_endian = data[3]
            self.size_of_int = data[4]
            self.size_of_size_t = data[5]
            self.size_of_instr = data[6]
            self.size_of_number = data[7]
            self.integral_flag = data[8]

            assert self.is_little_endian == True
            assert self.size_of_int == 4
            assert self.size_of_size_t == 4
            assert self.size_of_instr == 4
            assert self.size_of_number == 8

        def pack(self) -> bytearray:
            output = bytearray()
            output += struct.pack('<4sBB?BBBB?', self.magic, self.version, self.format_version, self.is_little_endian, self.size_of_int, self.size_of_size_t, self.size_of_instr, self.size_of_number, self.integral_flag)
            return output

    class Local:
        name: bytes
        start_pc: int
        end_pc: int

        def __init__(self, data: AccUnpack):
            self.name = data.unpack(f'{data.unpack("I")}s')
            self.start_pc = data.unpack("I")
            self.end_pc = data.unpack("I")

        def pack(self) -> bytearray:
            output = bytearray()
            output += struct.pack(f'<I{len(self.name)}sII', len(self.name), self.name, self.start_pc, self.end_pc)
            return output

    class Constant:
        vtype: int
        data = None

        def __init__(self, data: AccUnpack):
            self.vtype = data.unpack('B')
            if self.vtype == 0:
                pass # Nil
            elif self.vtype == 1:
                self.data = data.unpack('?')
            elif self.vtype == 3:
                self.data = data.unpack('d')
            elif self.vtype == 4:
                self.data = data.unpack(f'{data.unpack("I")}s')

        def pack(self) -> bytearray:
            output = bytearray()
            output += struct.pack('<B', self.vtype)
            if self.vtype == 0:
                pass # Nil
            elif self.vtype == 1:
                output += struct.pack('<?', self.data)
            elif self.vtype == 3:
                output += struct.pack('<d', self.data)
            elif self.vtype == 4:
                output += struct.pack(f'<I{len(self.data)}s', len(self.data), self.data)
            return output

    class Function:
        source: bytes
        line_defined: int
        last_line_defined: int
        number_of_upvalues: int
        number_of_parameters: int
        vararg_type: int
        max_stack_size: int
        code: list[int]
        consts: list['Luac.Const']
        funcs: list['Luac.Function']
        line_info: list[int]
        local_vars: list['Luac.Local']
        upvalues: list[bytes]

        def __init__(self, data: AccUnpack):
            self.source = data.unpack(f'{data.unpack("I")}s')
            self.line_defined = data.unpack('I')
            self.last_line_defined = data.unpack('I')
            self.number_of_upvalues = data.unpack('B')
            self.number_of_parameters = data.unpack('B')
            self.vararg_type = data.unpack('B')
            self.max_stack_size = data.unpack('B')
            self.code = data.unpack_list('I', data.unpack('I'))
            self.consts = [ Luac.Constant(data) for _ in range(data.unpack('I')) ]
            self.funcs = [ Luac.Function(data) for _ in range(data.unpack('I')) ]
            self.line_info = data.unpack_list('I', data.unpack('I'))
            self.local_vars = [ Luac.Local(data) for _ in range(data.unpack('I')) ]
            self.upvalues = [ data.unpack(f'{data.unpack("I")}s') for _ in range(data.unpack('I')) ]

        def pack(self) -> bytearray:
            output = bytearray()
            output += struct.pack(f'<I{len(self.source)}s', len(self.source), self.source)
            output += struct.pack('<I', self.line_defined)
            output += struct.pack('<I', self.last_line_defined)
            output += struct.pack('<B', self.number_of_upvalues)
            output += struct.pack('<B', self.number_of_parameters)
            output += struct.pack('<B', self.vararg_type)
            output += struct.pack('<B', self.max_stack_size)
            output += bytearray(itertools.chain.from_iterable([bytes(struct.pack('<I', len(self.code)))] + [ struct.pack('<I', code) for code in self.code ]))
            output += bytearray(itertools.chain.from_iterable([bytes(struct.pack('<I', len(self.consts)))] + [ const.pack() for const in self.consts ]))
            output += bytearray(itertools.chain.from_iterable([bytes(struct.pack('<I', len(self.funcs)))] + [ func.pack() for func in self.funcs ]))
            output += bytearray(itertools.chain.from_iterable([bytes(struct.pack('<I', len(self.line_info)))] + [ struct.pack('<I', line_info) for line_info in self.line_info ]))
            output += bytearray(itertools.chain.from_iterable([bytes(struct.pack('<I', len(self.local_vars)))] + [ local_var.pack() for local_var in self.local_vars ]))
            output += bytearray(itertools.chain.from_iterable([bytes(struct.pack('<I', len(self.upvalues)))] + [ struct.pack(f'<I{len(upvalue)}s', len(upvalue), upvalue) for upvalue in self.upvalues ]))
            return output

    def __init__(self, data_bytes: bytes):
        data = AccUnpack(data_bytes)

        self.header = data.unpack_list('4sBB?BBBB?', 1, Luac.Header)[0]
        self.func = Luac.Function(data)

    def pack(self):
        output = bytearray()
        output += self.header.pack()
        output += self.func.pack()
        return output