import struct, sys
from pathlib import Path


nnn_key = 0xFABACEDA
vlr_key = 0x1D153C0A


def div_to_chunks(L, n):
    """ Yield successive n-sized chunks from L """
    for i in range(0, len(L), n):
        yield L[i:i+n]

def unpack_acc(format, buffer, offset: list[1]):
    output = struct.unpack_from(format, buffer, offset[0])
    offset[0] += struct.calcsize(format)
    return output[0] if len(output) == 1 else output

def unpack_acc_list(format, buffer, offset: list[1], amount, data_class = None):
    output = []
    for _ in range(amount):
        if data_class:
            output += [ data_class(unpack_acc(format, buffer, offset)) ]
        else:
            output += [ unpack_acc(format, buffer, offset) ]
    return output


def decrypt(data: bytes, key: int, offset: int = 0) -> bytearray:
    output = bytearray()
    key_split = [ (key >> (count * 8)) & 0xFF for count in range(4) ] # Split key into 4 bytes

    for offset, dbyte in zip(range(offset, offset + len(data)), data):
        output += (dbyte ^ key_split[offset & 0b11] ^ (offset & 0xFF)).to_bytes()

    return output
encrypt = decrypt # Decrypting and encrypting uses the same algorithm

def hash_str(data: str) -> int:
    data_list = list(data.encode("ascii"))

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
    num: int
    unk: int

    def __init__(self, data):
        self.offset = data[0]
        self.key = data[1]
        self.size = data[2]
        self.num = data[3]
        self.unk = data[4]

class DirEntry:
    hashsum: int
    size: int
    offset: int

    def __init__(self, data):
        self.offset = data[0]
        self.key = data[1]
        self.size = data[2]

if __name__ == "__main__":
    key = nnn_key

    dir_hash_list = []

    fo = open("ze1_data.bin", "wb")

    fo.write(b"bin.")
    fo.write()