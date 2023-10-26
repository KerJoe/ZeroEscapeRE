from bm import BM
from bsm import BSM
from blender_model import BlenderModel
from pathlib import Path
from argparse import ArgumentParser
import os


parser = ArgumentParser(description='Zero Escape to Blender, model exporter')
parser.add_argument('output_file', type=Path, help='File path of ouput blender model')
parser.add_argument('input_files', type=Path, nargs='*', help='List of Zero Escape .bm, .bsm, .dds input files')
args = parser.parse_args()


if not args.input_files:
    print(f'No input files passed. Exiting.')
    exit(0)
for filepath in args.input_files:
    if not os.path.isfile(filepath):
        print(f'Input file "{filepath}" does not exist or is a folder.')
        exit(1)

if os.path.isdir(args.output_file):
    print("Output file is a folder.")
    exit(2)


model = BlenderModel(args.output_file.stem)
filepath: Path

for filepath in filter(lambda p: p.suffix == '.dds', args.input_files):
    print(f"Adding texture image: {filepath}")
    model.add_texture_image(filepath.stem, filepath)
print()

for filepath in filter(lambda p: p.suffix == '.bm', args.input_files):
    print(f"Adding simple model: {filepath}")
    bm = BM(open(filepath, 'rb').read())
    for bm_mesh in bm.meshes:
        mesh = model.add_mesh(filepath.stem)
        mesh.add_mesh([vert.geom_vert for vert in bm_mesh.verts], bm_mesh.indcs)
        mesh.add_normals([vert.norm_vert for vert in bm_mesh.verts])
        try:
            mesh.add_texture([vert.uv_vert for vert in bm_mesh.verts], Path(bm_mesh.texture_name).stem)
        except KeyError:
            if bm_mesh.texture_name:
                print(f'Texture "{Path(bm_mesh.texture_name).stem}.dds" was not found in input files, the mesh will be left untextured.')
    print()

bsm_armatures = []
for filepath in filter(lambda p: p.suffix == '.bsm', args.input_files):
    print(f"Adding rigged model: {filepath}")
    bsm = BSM(open(filepath, 'rb').read())
    bsm_armatures += [ bsm.armature ]
    for bsm_mesh in bsm.meshes:
        mesh = model.add_mesh(filepath.stem)
        mesh.add_mesh([vert.geom_vert for vert in bsm_mesh.verts], bsm_mesh.indcs)
        mesh.add_normals([vert.norm_vert for vert in bsm_mesh.verts])
        try:
            mesh.add_texture([vert.uv_vert for vert in bsm_mesh.verts], Path(bsm_mesh.texture_name).stem)
        except KeyError:
            if bsm_mesh.texture_name:
                print(f'Texture "{Path(bsm_mesh.texture_name).stem}.dds" was not found in input files, the mesh will be left untextured.')
        if not isinstance(bsm_mesh, BSM.ExtraMesh):
            bone_vert_groups = {}
            for bone in bsm_mesh.bones:
                bone_vert_groups[bsm.armature.plain[bone].proper_name] = []
            for vert_count, vert in enumerate(bsm_mesh.verts):
                bone_vert_groups[bsm.armature.plain[bsm_mesh.bones[vert.bone0]].proper_name] += [ (vert_count, vert.bone0_weight) ]
                bone_vert_groups[bsm.armature.plain[bsm_mesh.bones[vert.bone1]].proper_name] += [ (vert_count, vert.bone1_weight) ]
            mesh.add_bone_weights(bone_vert_groups)
    print()

# Combine all .bsm armatures into one
bones_list_raw = []
for armature in bsm_armatures:
    bones_list_raw += armature.plain
bones_dict = {}
for bone in bones_list_raw:
    if bone.proper_name in bones_dict.keys():
        continue
    bones_dict[bone.proper_name] = bone
children = {}
for bone in bones_dict:
    children[bone] = []
for armature in bsm_armatures:
    for parent in range(len(armature.children)):
        for child in armature.children[parent]:
            children[armature.plain[parent].proper_name] += [ armature.plain[child].proper_name ]
def traverse_bone_heir(bone, tree):
    for child in children[bone]:
        tree[child] = {}
        traverse_bone_heir(child, tree[child])
parentless_bones = []
all_bone_children = []
tree = {}
for children_value in children.values():
    all_bone_children += children_value
for bone in children:
    if not bone in all_bone_children:
        parentless_bones += [ bone ]
for bone in parentless_bones:
    tree[bone] = {}
    traverse_bone_heir(bone, tree[bone])
transform_dict = {}
for bone_name, bone_obj in bones_dict.items():
    transform_dict[bone_name] = bone_obj.transform
model.add_armature(tree, transform_dict)

model.save(args.output_file)