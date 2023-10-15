import struct, sys
from pathlib import Path


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


offset = [0]
filepath = Path("/home/misha/Games/ZeroEscape/ze1_data.bin")
if len(sys.argv) >= 2:
    filepath = Path(sys.argv[1]).absolute()
fi = open(filepath, "rb")
header_enc = fi.read(32)

if decrypt(header_enc[0:4], nnn_key) == b'bin.':
    print ("999 file detected")
    key = nnn_key
elif decrypt(header_enc[0:4], vlr_key) == b'bin.':
    print ("VLR file detected")
    key = vlr_key
else:
    print ("Unknown file detected")
    exit(1)


header = decrypt(header_enc, key)

unpack_acc('4s', header, offset)

meta_table_pos = unpack_acc('I', header, offset)
meta_data_pos = unpack_acc('I', header, offset)
data_pos = unpack_acc('Q', header, offset)

data_pos_copy = unpack_acc('Q', header, offset)
assert(data_pos == data_pos_copy)
unpack_acc('4x', header, offset)


meta = header + decrypt(fi.read(data_pos - 32), key, 32)

# Folder names ?
tmp_offset = offset[0]
meta_unk0_byte_size = unpack_acc('I', meta, offset)
meta_unk0_obj_size = unpack_acc('I', meta, offset)
unpack_acc('8x', meta, offset)
offset[0] = tmp_offset
unpack_acc(f'{meta_unk0_byte_size}x', meta, offset)

# Folder table ?
meta_unk1_byte_size = 16 * meta_unk0_obj_size
meta_unk1_obj_size = meta_unk0_obj_size
unpack_acc(f'{meta_unk1_byte_size}x', meta, offset)

# File names ?
tmp_offset = offset[0]
meta_unk2_byte_size = unpack_acc('I', meta, offset)
meta_unk2_obj_size = unpack_acc('I', meta, offset)
unpack_acc('8x', meta, offset)
offset[0] = tmp_offset
unpack_acc(f'{meta_unk2_byte_size}x', meta, offset)

# File table
meta_file_table_obj_size = meta_unk2_obj_size
meta_file_table = unpack_acc_list('= Q I Q I I 4x', meta, offset, meta_file_table_obj_size, FileEntry)


for file_count, file_entry in enumerate(meta_file_table):
    with open(Path(__file__).parent/filepath.stem/str(file_count), 'wb') as fo:
        fi.seek(data_pos + file_entry.offset)
        fo.write(decrypt(fi.read(file_entry.size), file_entry.key))
        print (f"Extracted file {file_count + 1} out of {len(meta_file_table)}")


fi.close()