# Blender exporter for Zero Escape models.
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

from bm import BM
from bsm import BSM
from bsn import BSN
from motion import Motion
from blender_model import BlenderModel
from pathlib import Path
from argparse import ArgumentParser
from treelib import Tree, Node
from helper import *
import os


parser = ArgumentParser(description='Zero Escape to Blender, model exporter')
parser.add_argument('output_file', type=Path, help='File path of ouput blender model')
parser.add_argument('input_files', type=Path, nargs='*', help='List of Zero Escape model file paths (Supported: .bm, .bsm, .dds)')
args = parser.parse_args()


model = BlenderModel(args.output_file.stem)


filepath: Path
model_objects: dict[str, list[object]] = {}

model_objects['dds'] = []
for filepath in filter(lambda p: p.suffix == '.dds', args.input_files):
    print(f"Adding texture image: {filepath}")
    model.add_texture_image(filepath.stem, filepath)
    model_objects['dds'] += [ filepath.stem ]
print()

model_objects['bm'] = []
for filepath in filter(lambda p: p.suffix == '.bm', args.input_files):
    print(f"Adding simple model: {filepath}")
    bm = BM(try_open(filepath, 'rb').read())
    model_objects['bm'] += [ bm ]

    for bm_mesh in bm.meshes:
        mesh = model.add_mesh(filepath.stem)
        mesh.add_geometry(bm_mesh.verts, bm_mesh.indcs)
        mesh.add_normals(bm_mesh.verts)
        try:
            mesh.add_texture(bm_mesh.verts, bm_mesh.texture_name)
        except KeyError:
            if bm_mesh.texture_name:
                print(f'Texture "{Path(bm_mesh.texture_name).stem}.dds" was not found in input files, the mesh will be left untextured.')
    print()

model_objects['bsm'] = []
for filepath in filter(lambda p: p.suffix == '.bsm', args.input_files):
    print(f"Adding rigged model: {filepath}")
    bsm = BSM(try_open(filepath, 'rb').read())
    model_objects['bsm'] += [ bsm ]

    for bsm_mesh in bsm.meshes:
        mesh = model.add_mesh(filepath.stem)
        mesh.add_geometry(bsm_mesh.verts, bsm_mesh.indcs)
        mesh.add_normals(bsm_mesh.verts)
        try:
            mesh.add_texture(bsm_mesh.verts, bsm_mesh.texture_name)
        except (KeyError, AttributeError):
            if bsm_mesh.texture_name:
                print(f'Texture "{Path(bsm_mesh.texture_name).stem}.dds" was not found in input files, the mesh will be left untextured.')
        mesh.add_bone_weights(bsm.armature.bones, bsm_mesh.verts, bsm_mesh.bones)
        mesh.add_shapekeys(bsm_mesh.animations, bsm_mesh.verts)
    print()

bsn_files = list(filter(lambda p: p.suffix == '.bsn', args.input_files))
if bsn_files:
    filepath = bsn_files[0]
    if len(bsn_files) > 1:
        print(f"More than one .bsn file passed. Using only '{filepath}'.")

    print(f"Using structure file {filepath}")
    bsn = BSN(try_open(filepath, 'rb').read())
    model_objects['bsn'] = bsn

# Combine all .bsm armatures into one
armature = Tree(); armature.create_node('@', '@')
bsm: BSM
# Flatten tree and deduplicate bones
for bsm in model_objects['bsm']:
    for bone in bsm.armature.bones.expand_tree():
        bone_node: Node = bsm.armature.bones[bone]
        if (bone_node.tag in armature) or bone_node.is_root():
            continue
        armature.create_node(bone_node.tag, bone_node.tag, data=bone_node.data, parent='@')
# Recreate tree stucture
for bsm in model_objects['bsm']:
    for bone in bsm.armature.bones.expand_tree():
        bone_node: Node = bsm.armature.bones[bone]
        if bone_node.is_root() or (bsm.armature.bones.parent(bone) == bsm.armature.bones.root):
            continue
        armature.move_node(bone_node.tag, bsm.armature.bones.parent(bone).tag)
if model_objects['bsm'] != []:
    print(f"Combined armature tree:")
    print(armature.show(stdout=False))
    model.add_armature(armature)


motion_files = list(filter(lambda p: p.suffix == '.motion', args.input_files))
if motion_files:
    filepath = motion_files[0]
    if len(bsn_files) > 1:
        print(f"More than one .motion file passed. Using only '{filepath}'.")

    print(f"Adding animator: {filepath}")
    motion = Motion(try_open(filepath, 'rb').read())
    model_objects['motion'] = motion

    model.add_animation(motion.dynamics)
    print()


model.save(args.output_file)