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
from copy import deepcopy
from argparse import ArgumentParser
from treelib import Tree, Node
from helper import *
import math, mathutils


filepath: Path
bsm: BSM
bm: BM
bsn: BSN
model_objects: dict[str, list[object]] = {}


parser = ArgumentParser(description='Zero Escape to Blender, model exporter')
parser.add_argument('output_file', type=Path, help='Output path of the generated Blender file')
parser.add_argument('input_files', type=Path, nargs='*', help='List of Zero Escape input model files (Supported extensions: .bm, .bsm, .bsn, .dds, .motion)')
args = parser.parse_args()


model = BlenderModel(args.output_file.stem)


model_objects['dds']: list[str] = []
for filepath in filter(lambda p: p.suffix == '.dds', args.input_files):
    print(f'Adding texture image: "{filepath}"')
    model.add_texture_image(filepath.stem, filepath)
    model_objects['dds'] += [ filepath.stem ]

print()


model_objects['bm']: dict[str, BM] = {}
for filepath in filter(lambda p: p.suffix == '.bm', args.input_files):
    print(f'Adding simple model: "{filepath}"')
    bm = BM(try_open(filepath, 'rb').read())
    model_objects['bm'][filepath.stem] = bm

    for bm_mesh in bm.meshes:
        mesh = model.add_mesh(filepath.stem)
        mesh.add_geometry(bm_mesh.verts, bm_mesh.indcs)
        mesh.add_normals(bm_mesh.verts)
        try:
            if bm_mesh.texture_name:
                mesh.add_texture(bm_mesh.verts, bm_mesh.texture_name)
        except (KeyError, AttributeError):
            print(f'Texture "{Path(bm_mesh.texture_name).stem}.dds" was not found among input files, the mesh will be left untextured')

    print()


model_objects['bsm']: dict[str, BSM] = {}
for filepath in filter(lambda p: p.suffix == '.bsm', args.input_files):
    print(f'Adding rigged model: "{filepath}"')
    bsm = BSM(try_open(filepath, 'rb').read())
    model_objects['bsm'][filepath.stem] = bsm

    for bsm_mesh in bsm.meshes:
        mesh = model.add_mesh(filepath.stem)
        mesh.add_geometry(bsm_mesh.verts, bsm_mesh.indcs)
        mesh.add_normals(bsm_mesh.verts)
        try:
            if bsm_mesh.texture_name:
                mesh.add_texture(bsm_mesh.verts, bsm_mesh.texture_name)
        except (KeyError, AttributeError):
            print(f'Texture "{Path(bsm_mesh.texture_name).stem}.dds" was not found in input files, the mesh will be left untextured')
        mesh.add_bone_weights(bsm.armature.bones, bsm_mesh.verts, bsm_mesh.bones)
        mesh.add_shapekeys(bsm_mesh.animations, bsm_mesh.verts)

    print()

model_objects['bsn'] = None
bsn_files = list(filter(lambda p: p.suffix == '.bsn', args.input_files))
if bsn_files:
    filepath = bsn_files[0]
    if len(bsn_files) > 1:
        print(f'More than one .bsn file passed. Using only "{filepath}".')

    print(f'Using structure file: {filepath}')
    bsn = BSN(try_open(filepath, 'rb').read())
    model_objects['bsn'] = bsn


# TODO: Find a way to get the correct static position of bsn only bones
# Combine all .bsm armatures into one
bsm_armature = Tree(); bsm_armature.create_node('@', '@')
# Flatten the tree and deduplicate bones
for bsm in model_objects['bsm'].values():
    for bone in bsm.armature.bones.expand_tree():
        bone_node: Node = bsm.armature.bones[bone]
        if bone_node.is_root(): # Skip if root
            continue
        # Override bone data if it has a parent among bsm armatures
        if bone_node.tag in bsm_armature: # If bone already added
            if not bsm.armature.bones.parent(bone_node.identifier).is_root(): # If bone is not parentless
                bsm_armature[bone_node.tag].data = bone_node.data
            continue
        bsm_armature.create_node(bone_node.tag, bone_node.tag, data=bone_node.data, parent='@')
# Recreate the tree structure
if not model_objects['bsn']:
    for bsm in model_objects['bsm'].values():
        for bone in bsm.armature.bones.expand_tree():
            bone_node: Node = bsm.armature.bones[bone]
            # If not root or the bone is parentless, move it to its parent
            if bone_node.is_root() or bsm.armature.bones.parent(bone).is_root():
                continue
            bsm_armature.move_node(bone_node.tag, bsm.armature.bones.parent(bone).tag)
    armature = bsm_armature
else:
    bsn_armature = Tree(model_objects['bsn'].scene_entries, deep=True)
    # Remove mesh nodes and their parents
    for entry in bsn_armature.expand_tree():
        entry_node: Node = bsn_armature[entry]
        if bsn_armature.children(entry):
            if bsn_armature.children(entry)[0].data.type_name in [ 'mesh', 'amsh' ]:
                bsn_armature.remove_node(bsn_armature.children(entry)[0].identifier)
                bsn_armature.remove_node(entry)
                continue
    # Remove unnescesarry VisualSceneNode and root entries
    if 'VisualSceneNode' in bsn_armature:
        bsn_armature.link_past_node('VisualSceneNode')
    if 'root' in bsn_armature:
        bsn_armature.link_past_node('root')

    for entry in bsn_armature.expand_tree():
        entry_node: Node = bsn_armature[entry]
        if entry in bsm_armature: #
            entry_node.data = deepcopy(bsm_armature[entry].data)

            # Skip if root
            if not bsn_armature.parent(entry):
                continue

            # Test if bone is parentless in every bsm file
            always_root = True
            for bsm in model_objects['bsm'].values():
                for bone in bsm.armature.bones.all_nodes():
                    if entry == bone.tag:
                        if bsm.armature.bones.parent(bone.identifier):
                            if not bsm.armature.bones.parent(bone.identifier).is_root():
                                always_root = False
            # If it is we must replace its absolute offset with the relative bsn offset
            if always_root:
                if bsn_armature.parent(entry):
                    if not bsn_armature.parent(entry).is_root():
                        entry_node.data.transform = ( \
                                (entry_node.data.transform[0][0], entry_node.data.transform[0][1], entry_node.data.transform[0][2], model_objects['bsn'].scene_entries[entry].data.offset[0]), \
                                (entry_node.data.transform[1][0], entry_node.data.transform[1][1], entry_node.data.transform[1][2], model_objects['bsn'].scene_entries[entry].data.offset[1]), \
                                (entry_node.data.transform[2][0], entry_node.data.transform[2][1], entry_node.data.transform[2][2], model_objects['bsn'].scene_entries[entry].data.offset[2]), \
                                (entry_node.data.transform[3][0], entry_node.data.transform[3][1], entry_node.data.transform[3][2], 1.0), \
                            )
        else:
            # Bridge the gaps between bsm armatures with bones from bsn
            #
            class SceneBone:
                internal_name: str
                proper_name: str
                transform: list[list[float]]

            # Convert bsn bone offset (without rotation and scale) into a matrix
            bone = SceneBone()
            bone.internal_name = ''
            bone.proper_name = entry
            bone.transform = mathutils.Matrix.Translation(mathutils.Vector(entry_node.data.offset))
            entry_node.data = bone
    armature = bsn_armature
if model_objects['bsm'] != {} or model_objects['bsn']:
    print('Combined armature tree:')
    print(armature.show(stdout=False))
    model.add_armature(armature)


if bsn_files:
    def absolute_armature(name: str) -> list[tuple[float, float, float]]:
        """ Calculate absolute position and rotation of a bone by traversing the armature """
        # HACK: Prefer bsm armature over bsn
        for bsm in model_objects['bsm'].values():
            for bone in bsm.armature.bones.all_nodes():
                if bone.tag == name:
                    traversal_armature = bsm.armature.bones
                    traversal_order = list(bsm.armature.bones.rsearch(bone.identifier))
                    break
            else:
                continue
            break
        else:
            traversal_armature = armature
            traversal_order = list(armature.rsearch(name))
        traversal_order.reverse() # Reverse order to get for the parent to child sequence of matrix multiplications

        matrix = mathutils.Matrix.Identity(4)
        for bone in traversal_order:
            if traversal_armature[bone].data:
                matrix @= mathutils.Matrix(traversal_armature[bone].data.transform)
        td = matrix.decompose()
        pos_x, pos_y, pos_z = td[0]
        rot_x, rot_y, rot_z = td[1].to_euler('XYZ')
        rot_x = math.degrees(rot_x); rot_y = math.degrees(rot_y); rot_z = math.degrees(rot_z)
        return [ (pos_x, pos_y, pos_z), (rot_x, rot_y, rot_z) ]

    # Assign simple model files to bones and set their position
    for bm_name in model_objects['bm'].keys():
        if bm_name in bsn.scene_entries:
            bm_obj_name = bsn.scene_entries.parent(bm_name).identifier
            bm_bone_name = bsn.scene_entries.parent(bm_obj_name).identifier

            sub_meshes = filter(lambda mesh: mesh.name.startswith(f'{bm_name}.') or mesh.name == bm_name, model.meshes)
            for mesh in sub_meshes:
                print(f'Assigning "{mesh.mesh.name}" to bone "{bm_bone_name}"')
                mesh.add_single_bone_weight(bm_bone_name, 1.0)

                pos_rot = absolute_armature(bm_bone_name)
                mesh.mesh_obj.location = ( pos_rot[0][0] + bsn.scene_entries[bm_obj_name].data.offset[0], pos_rot[0][1] + bsn.scene_entries[bm_obj_name].data.offset[1], pos_rot[0][2] + bsn.scene_entries[bm_obj_name].data.offset[2] )
                mesh.mesh_obj.rotation_euler = mathutils.Euler((math.radians(bsn.scene_entries[bm_obj_name].data.rotation[0]), math.radians(bsn.scene_entries[bm_obj_name].data.rotation[1]), math.radians(bsn.scene_entries[bm_obj_name].data.rotation[2])), 'XYZ')
                mesh.mesh_obj.scale = bsn.scene_entries[bm_obj_name].data.size

    print()


motion_files = list(filter(lambda p: p.suffix == '.motion', args.input_files))
if motion_files:
    filepath = motion_files[0]
    if len(bsn_files) > 1:
        print(f'More than one .motion file passed, using only "{filepath}"')

    print(f'Adding animator: "{filepath}"')
    motion = Motion(try_open(filepath, 'rb').read())
    model_objects['motion'] = motion

    model.add_dynamic_animations(motion.dynamics)
    model.add_static_animations(motion.statics, armature)
    model.add_morph_animations(motion.morphs)

    print()

model.save(args.output_file)
