import sys, struct, math
from pathlib import Path


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


class BMVerts:
    geom_vert:       (float, float, float) # 12 bytes
    norm_vert:       (float, float, float) # 12 bytes
    uv_vert:         (float, float) # 12 bytes # First value is NaN

    def __init__(self, data):
        self.geom_vert      = (data[0], data[1], data[2])
        self.norm_vert      = (data[3], data[4], data[5])
        self.uv_vert        = (data[7], data[8])

        assert(math.isnan(data[6]))

class Mesh:
    verts: list[BMVerts]
    indcs: list[int]
    texture_name: str

    def __init__(self, data, offset):
        unpack_acc("4x", data, offset)

        indc_amount = unpack_acc("I", data, offset)
        self.indcs = unpack_acc_list("hhh", data, offset, indc_amount//3)
        print (f"- {indc_amount} indices")

        vert_amount = unpack_acc("I", data, offset)
        self.verts = unpack_acc_list("3f 3f 3f", data, offset, vert_amount, BMVerts)
        print (f"- {vert_amount} vertecies")

        unpack_acc("53x", data, offset)

        texture_name_size = unpack_acc("I", data, offset)
        self.texture_name = unpack_acc(f"{texture_name_size}s", data, offset).decode("ascii")
        print (f"- Texture: {self.texture_name}")

        unpack_acc("36x", data, offset)


filepath = "/home/misha/Documents/Projects/ZeroEscapeRE/model_converter/extracted_models/scenes/chara/phi/mdl/md_hairShape.bm"
if len(sys.argv) >= 2:
    filepath = Path(sys.argv[1]).absolute()
filename = Path(filepath).stem


offset = [0]
print(f"Loading model {filepath}")
f = open(filepath, "rb")
data = f.read()
f.close()


mesh_amount = unpack_acc("I", data, offset)
meshes: list[Mesh] = []
print (f"Model contains {mesh_amount} mesh(es):")
for mesh_count in range(mesh_amount):
    print (f"Mesh {mesh_count}:")
    new_mesh = Mesh(data, offset)
    meshes += [ new_mesh ]


import bpy

bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True) # Remove default cube
for mesh_count, mesh in enumerate(meshes):
    bmesh = bpy.data.meshes.new(f"{filename}_{mesh_count}")
    obj = bpy.data.objects.new(bmesh.name, bmesh)
    col = bpy.data.collections["Collection"]
    col.objects.link(obj)
    bpy.context.view_layer.objects.active = obj

    bmesh.from_pydata([vert.geom_vert for vert in mesh.verts], [], mesh.indcs)

    bmesh.normals_split_custom_set_from_vertices([vert.norm_vert for vert in mesh.verts])
    #bmesh.use_auto_smooth = True

    bmesh_uv = bmesh.uv_layers.new()
    for face in bmesh.polygons:
        for vert, loop in zip(face.vertices, face.loop_indices):
            bmesh_uv.data[loop].uv = ( mesh.verts[vert].uv_vert[0], 1 - mesh.verts[vert].uv_vert[1]) # V is inverted

    image = bpy.data.images.load(f"{Path(__file__).parent}/extracted_models/{Path(mesh.texture_name).with_suffix('.dds')}")
    image.pack()

    material = material = bpy.data.materials.new(Path(mesh.texture_name).stem)
    material.use_nodes = True

    texture = material.node_tree.nodes.new('ShaderNodeTexImage')
    texture.image = image

    bsdf = material.node_tree.nodes["Principled BSDF"]
    material.node_tree.links.new(bsdf.inputs['Base Color'], texture.outputs['Color'])
    material.node_tree.links.new(bsdf.inputs['Alpha'], texture.outputs['Alpha'])
    material.blend_method = "CLIP"

    bmesh.materials.append(material)


bpy.ops.wm.save_as_mainfile(filepath=f"{Path(__file__).parent}/converted_models/{filename}.blend")