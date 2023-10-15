import struct

nnn_key = 0xFABACEDA
vlr_key = 0x1D153C0A

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

offset = [0]
f = open("/home/misha/Games/ZeroEscape/ze1_data.bin", "rb")
header = decrypt(f.read(48), nnn_key)

unpack_acc()



    # key_split = [ (key >> (2**(count*8))) & 0xFF for count in range(4) ] # Split key into 4 bytes
    # rolling_key_split = [ offset + count for count in range(4) ]

    # for u32 in div_to_chunks(data, 4):
    #     u32_split = [ int.from_bytes(u8) for u8 in u32]

    #     output[]
