import bpy
import struct
import sys
from pathlib import Path

filepath = '/home/misha/Documents/Projects/ZeroEscapeRE/model_converter/extracted_models/scenes/chara/phi/mdl/md_arm_LShape-skin.bsm'
if len(sys.argv) >= 2:
    filepath = Path(sys.argv[1]).absolute()

filename = Path(filepath).stem

b2i = lambda data, start, size: int.from_bytes(data[start:start+size], byteorder="little")
b2f = lambda data, start: struct.unpack("<f", data[start:start+4])[0]
b2s = lambda data, start, max_size=None: data[start:(start + max_size) if max_size else None].decode("ascii").rstrip("\x00")

def div_to_chunks(L, n):
    """ Yield successive n-sized chunks from L """
    for i in range(0, len(L), n):
        yield L[i:i+n]

f = open(filepath, "rb")
fc = f.read()

face_count_pos = 8; face_count_size = 4
face_start = face_count_pos + face_count_size; face_size = 2
face_count = b2i(fc, face_count_pos, face_count_size)

vert_count_pos = face_start + face_size*face_count; vert_count_size = 4
vert_start = vert_count_pos + vert_count_size; vert_size = 4
vert_block_size = 9
vert_count = b2i(fc, vert_count_pos, vert_count_size) * vert_block_size

texture_name_start = vert_start + vert_count*vert_size + 57; texture_name_max_size = 40

faces = []
for face_i in range(face_start, face_start + face_count*face_size, face_size*3): # Three verteces per face
    face = []
    for vert_i in range(3):
        face += [ b2i(fc, face_i + face_size*vert_i, face_size) ]
    faces += [ tuple(face) ]

verts = []
for vert_i in range(vert_start, vert_start + vert_count*vert_size, vert_size):
    verts += [ b2f(fc, vert_i) ]

geom_verts = []
unk_verts = []
uv_verts = []
for vert in div_to_chunks(verts, vert_block_size):
    geom_verts += [( vert[0], vert[1], vert[2] )]
    unk_verts  += [( vert[3], vert[4], vert[5] )]
    uv_verts   += [( vert[7], 1 - vert[8] )] # vert[6] is NaN

texture_name = b2s(fc, texture_name_start, texture_name_max_size)

mesh = bpy.data.meshes.new(filename)
obj = bpy.data.objects.new(mesh.name, mesh)
col = bpy.data.collections["Collection"]
col.objects.link(obj)
bpy.context.view_layer.objects.active = obj

bpy.data.objects.remove(bpy.data.objects['Cube'], do_unlink=True) # Remove default cube

mesh.from_pydata(geom_verts, [], faces)

uv = mesh.uv_layers.new()
for face in mesh.polygons:
    for vert, loop in zip(face.vertices, face.loop_indices):
        uv.data[loop].uv = uv_verts[vert]

image = bpy.data.images.load(f"{Path(__file__).parent}/extracted_models/{Path(texture_name).with_suffix('.dds')}")
image.pack()

material = material = bpy.data.materials.new('bangle')
material.use_nodes = True

texture = material.node_tree.nodes.new('ShaderNodeTexImage')
texture.image = image

bsdf = material.node_tree.nodes["Principled BSDF"]
material.node_tree.links.new(bsdf.inputs['Base Color'], texture.outputs['Color'])

mesh.materials.append(material)

bpy.ops.wm.save_as_mainfile(filepath=f"{Path(__file__).parent}/converted_models/{filename}.blend")
