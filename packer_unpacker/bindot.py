# Zero Escape BinDot (game resource .bin file) data class.
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

import math
from helper import *
from io import IOBase
import xor_cipher

# A Zero Escape data file has a 'bin.' magic header
# So let's make it the format name
class BinDot:

    def crypt(data: bytes, key: int, offset: int = 0) -> bytearray:
        """ Zero Escape file data decryption/encryption algorithm """

        output = bytearray()
        key_split = [ (key >> (count * 8)) & 0xFF for count in range(4) ] # Split key into 4 bytes

        for offset, dbyte in zip(range(offset, offset + len(data)), data):
            output += (dbyte ^ key_split[offset & 0b11] ^ (offset & 0xFF)).to_bytes()

        return output

    def crypt_optimized(data: bytes, key: int, offset: int = 0) -> bytes:
        """ Zero Escape file data decryption/encryption algorithm """

        if offset:
            mask = xor_cipher.cyclic_xor_unsafe( \
                bytes(range(offset&0xFF, 256)) + bytes(range(0, offset&0xFF)), \
                key.to_bytes(4, 'little')[offset&0b11:4] + key.to_bytes(4, 'little')[0:offset&0b11])
        else:
            mask = xor_cipher.cyclic_xor_unsafe(bytes(range(256)), key.to_bytes(4, 'little'))

        return xor_cipher.cyclic_xor_unsafe(bytes(data), mask)

    # Decryption and encryption uses the same algorithm
    encrypt = crypt_optimized
    decrypt = crypt_optimized


    def hash_str(data: str) -> int:
        """ Zero Escape file name hashing algorithm (Directory hash: /dir, File Hash: /dir/file.ext) """

        data_list = list(data.encode('ascii'))

        hashsum = 0
        for char_pair in div_to_chunks(data_list, 2):
            if len(char_pair) == 2:
                hashsum = ((char_pair[0] & 0xDF) + hashsum * 0x83) * 0x83 + (char_pair[1] & 0xDF)
            else:
                hashsum = hashsum * 0x83 + (char_pair[0] & 0xDF)

        charsum = 0
        for char in data_list:
            charsum += char

        return ((hashsum << 4) & 0x7FFFFFF0) | (charsum & 0xF)


    class FileEntry:
        offset: int
        key: int
        size: int
        index: int
        flags: int
        name_hash: int

        def __init__(self, data):
            self.offset = data[0]
            self.key = data[1]
            self.size = data[2]
            self.index = data[3]
            self.flags = data[4]


    class DirEntry:
        name_hash: str
        size: int
        offset: int
        files: list['BinDot.FileEntry']

        def __init__(self, data):
            self.name_hash = data[0]
            self.size = data[1]
            self.offset = data[2]


    nnn_key = 0xFABACEDA
    vlr_key = 0x1D153C0A

    key: int = None
    directories: list['BinDot.DirEntry'] = []


    def open(self, file: IOBase, key: int=None):
        magic_enc = file.read(4) # 4 bytes: Magic number 'bin.'

        if key is None:
            key = self.key
        if key is None:
            # Auto detect file key
            if BinDot.decrypt(magic_enc, self.nnn_key) == b'bin.':
                print ('999 BinDot file detected.')
                self.key = self.nnn_key
            elif BinDot.decrypt(magic_enc, self.vlr_key) == b'bin.':
                print ('VLR BinDot file detected.')
                self.key = self.vlr_key
            else:
                raise Exception('Unknown BinDot file detected.')
        else:
            self.key = key
        assert(BinDot.decrypt(magic_enc, self.key) == b'bin.')

        header = AccUnpack(BinDot.decrypt(file.read(28), self.key, 4))

        self.dir_names_pos = header.unpack('I') # 4 bytes: Folder name hashes list offset
        assert(self.dir_names_pos == 32)
        self.file_names_pos = header.unpack('I') # 4 bytes File name hashes list offset
        self.data_pos = header.unpack('Q') # 8 bytes: File data offset

        data_pos_copy = header.unpack('Q') # 4 bytes: Copy of data_pos
        assert(self.data_pos == data_pos_copy)

        header.unpack('4x') # 4 bytes: Padding


        meta = AccUnpack(BinDot.decrypt(file.read(self.data_pos - self.dir_names_pos), self.key, self.dir_names_pos))

        # Folder name hashes
        dir_names_offset = meta.offset
        dir_names_byte_size = meta.unpack('I') # 4 bytes: Size of folder name hashes list in bytes (with padding and including this 16 byte header)
        dir_amount = meta.unpack('I') # 4 bytes: Amount of folders
        meta.unpack('8x') # 8 bytes: Padding
        dir_names = meta.unpack_list('I', dir_amount)
        meta.offset = dir_names_offset + dir_names_byte_size

        # Folder allocation table
        dir_table = meta.unpack_list('I I I 4x', dir_amount, self.DirEntry)

        # File name hashes
        file_names_offset = meta.offset
        file_names_byte_size = meta.unpack('I') # 4 bytes: Size of file name hashes list in bytes (with padding and including this 16 byte header)
        file_amount = meta.unpack('I') # 4 bytes: Amount of files
        meta.unpack('8x') # 8 bytes: Padding
        file_names = meta.unpack_list('I', file_amount)
        meta.offset = file_names_offset + file_names_byte_size

        # File allocation table
        file_table = meta.unpack_list('Q I Q I I 4x', file_amount, self.FileEntry)


        for count, name in enumerate(dir_names):
            assert(dir_table[count].name_hash == name) # Assert that hashes in list of folder hashes and folder allocation table are the same
        for count, file_name in enumerate(file_names):
            file_table[count].name_hash = file_name


        self.directories = dir_table
        for directory_entry in self.directories:
            directory_entry.files = []
            for file_entry in range(directory_entry.offset, directory_entry.offset + directory_entry.size):
                directory_entry.files += [ file_table[file_entry] ]


    def read(self, file: IOBase, file_entry: FileEntry) -> bytes:
        file.seek(self.data_pos + file_entry.offset)
        return BinDot.decrypt(file.read(file_entry.size), file_entry.key)


    def save(self, file: IOBase, key: int=None):
        if self.key is None:
            self.key = key
        if self.key is None:
            raise Exception('No BinDot key set')

        self.dir_names_pos = 32

        dir_amount = len(self.directories)
        dir_names_byte_size = math.ceil((dir_amount*4 + 16) / 16) * 16
        self.file_names_pos = self.dir_names_pos + dir_names_byte_size + dir_amount*16

        files = []
        for directory_entry in self.directories:
            files += directory_entry.files
        file_amount = len(files)
        file_names_byte_size = math.ceil((file_amount * 4 + 16) / 16) * 16
        self.data_pos = self.file_names_pos + file_names_byte_size + file_amount*32

        header = struct.pack('< 4s I I Q Q  I', b'bin.', self.dir_names_pos, self.file_names_pos, self.data_pos, self.data_pos, 0xFFFFFFFF)
        file.write(BinDot.encrypt(header, self.key, file.tell()))

        dir_names = bytearray()
        dir_names += struct.pack('< I I  Q', dir_names_byte_size, dir_amount, 0xFFFFFFFFFFFFFFFF)
        for directory_entry in self.directories:
            dir_names += struct.pack('< I', directory_entry.name_hash)
        dir_names += struct.pack(f'{dir_names_byte_size - dir_amount*4 - 16}x')
        file.write(BinDot.encrypt(dir_names, self.key, file.tell()))

        dir_table = bytearray()
        for directory_entry in self.directories:
            dir_table += struct.pack('< I I I  I', directory_entry.name_hash, directory_entry.size, directory_entry.offset, 0xFFFFFFFF)
        file.write(BinDot.encrypt(dir_table, self.key, file.tell()))

        file_names = bytearray()
        file_names += struct.pack('< I I  Q', file_names_byte_size, file_amount, 0xFFFFFFFFFFFFFFFF)
        for file_entry in files:
            file_names += struct.pack('< I', file_entry.name_hash)
        file_names += struct.pack(f'{file_names_byte_size - file_amount*4 - 16}x')
        file.write(BinDot.encrypt(file_names, self.key, file.tell()))

        file_table = bytearray()
        for file_entry in files:
            file_table += struct.pack('< Q I Q I I  I', file_entry.offset, file_entry.key, file_entry.size, file_entry.index, file_entry.flags, 0xFFFFFFFF)
        file.write(BinDot.encrypt(file_table, self.key, file.tell()))


    def write(self, data: bytes, file: IOBase, file_entry: FileEntry):
        file.seek(self.data_pos + file_entry.offset)
        file.write(BinDot.encrypt(data, file_entry.key))
