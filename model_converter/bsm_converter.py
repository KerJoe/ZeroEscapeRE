import bpy
import struct
import sys
from pathlib import Path

b2i = lambda data, start, size: int.from_bytes(data[start:start+size], byteorder=("little"))
b2f = lambda data, start: struct.unpack("<f", data[start:start+4])[0]
b2s = lambda data, start, max_size=None: data[start:(start + max_size) if max_size else None].decode("ascii").rstrip("\x00")

#filepath = "/home/misha/Documents/Projects/ZeroEscapeRE/model_converter/extracted_models/scenes/chara/dio/mdl/md_arm_LShape-skin.bsm"
filepath = '/home/misha/Documents/Projects/ZeroEscapeRE/model_converter/extracted_models/scenes/chara/phi/mdl/md_necklaceShape-skin.bsm'
if len(sys.argv) >= 2:
    filepath = Path(sys.argv[1]).absolute()

filename = Path(filepath).stem

def div_to_chunks(L, n):
    """ Yield successive n-sized chunks from L """
    for i in range(0, len(L), n):
        yield L[i:i+n]

f = open(filepath, "rb")
fc = f.read()

vert_count_pos = 16; vert_count_size = 4
#vert_count_pos = 0x3a39; vert_count_size = 4
vert_start = vert_count_pos + vert_count_size; vert_size = 4
vert_block_size = 14
vert_count = b2i(fc, vert_count_pos, vert_size) * vert_block_size

face_count_pos = vert_start + vert_size*vert_count + 4; face_count_size = 4
face_start = face_count_pos + face_count_size; face_size = 2
face_count = b2i(fc, face_count_pos, face_count_size)

unk0_count_pos = face_start + face_count*face_size; unk0_count_size = 4
unk0_start = unk0_count_pos + unk0_count_size; unk0_size = 4
unk0_count = b2i(fc, unk0_count_pos, unk0_count_size)

texture_name_start = unk0_start + unk0_count*unk0_size + 121; texture_name_max_size = 40

verts = []
unk1 = []
for vert_i in range(vert_start, vert_start + vert_count*vert_size, vert_size):
    verts += [ b2f(fc, vert_i) ]
    if ((vert_i - vert_start) / 4) % vert_block_size == 9:
        unk1 += [( b2i(fc, vert_i, 1), b2i(fc, vert_i+1, 1), b2i(fc, vert_i+2, 1), b2i(fc, vert_i+3, 1) )]

geom_verts = []
unk0_verts = []
uv_verts = []
for vert in div_to_chunks(verts, vert_block_size):
    geom_verts += [( vert[0], vert[1], vert[2] )]
    unk0_verts += [( vert[3], vert[4], vert[5] )]
    uv_verts   += [( vert[7], 1 - vert[8] )] # vert[6] is NaN

faces = []
for face_i in range(face_start, face_start + face_count*face_size, face_size*3): # Three verteces per face
    face = []
    for vert_i in range(3):
        face += [ b2i(fc, face_i + face_size*vert_i, face_size) ]
    faces += [ tuple(face) ]

texture_name = b2s(fc, texture_name_start, texture_name_max_size)

mesh = bpy.data.meshes.new(filename)
obj = bpy.data.objects.new(mesh.name, mesh)
col = bpy.data.collections["Collection"]
col.objects.link(obj)
bpy.context.view_layer.objects.active = obj

bpy.data.objects.remove(bpy.data.objects['Cube'], do_unlink=True) # Remove default cube

mesh.from_pydata(geom_verts, [], faces)


# uv = mesh.uv_layers.new()
# for face in mesh.polygons:
#     for vert, loop in zip(face.vertices, face.loop_indices):
#         uv.data[loop].uv = uv_verts[vert]

# image = bpy.data.images.load(f"{Path(__file__).parent}/extracted_models/{Path(texture_name).with_suffix('.dds')}")
# image.pack()

# material = material = bpy.data.materials.new(Path(texture_name).stem)
# material.use_nodes = True

# texture = material.node_tree.nodes.new('ShaderNodeTexImage')
# texture.image = image

# bsdf = material.node_tree.nodes["Principled BSDF"]
# material.node_tree.links.new(bsdf.inputs['Base Color'], texture.outputs['Color'])
# material.node_tree.links.new(bsdf.inputs['Alpha'], texture.outputs['Alpha'])

# mesh.materials.append(material)


colors = []
for r in range(4):
    for g in range(4):
        for b in range(4):
            colors += [( 1.0/3*r, 1.0/3*g, 1.0/3*b, 1.0 )]

material = bpy.data.materials.new(f"Base")
material.diffuse_color = (1.0, 1.0, 1.0, 1.0)
mesh.materials.append(material)

mats = [0] * len(colors)
for color_count, color in enumerate(colors):
    mats[color_count] = bpy.data.materials.new(f"{color_count}")
    mats[color_count].diffuse_color = color
    mesh.materials.append(mats[color_count])

for gvert_count, gvert in enumerate(geom_verts):
    for face_count, face in enumerate(mesh.polygons):
        if gvert_count in face.vertices:
            face.material_index = unk1[gvert_count][0] + 1


bpy.ops.wm.save_as_mainfile(filepath=f"{Path(__file__).parent}/converted_models/{filename}.blend")
