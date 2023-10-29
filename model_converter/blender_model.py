# BlenderModel class, creates a blender model from Zero Escape model data.
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

import bpy, mathutils
from pathlib import Path
from bm import BM
from bsm import BSM
from treelib import Tree, Node


class BlenderModel():
    class Mesh:
        name: str
        mesh: bpy.types.Mesh
        mesh_obj: bpy.types.Object

        def __init__(self, name: str):
            self.name = name
            self.mesh = bpy.data.meshes.new(f"{name}.mesh") # Meshes after first will have ".###" automatically appended
            self.mesh_obj = bpy.data.objects.new(self.mesh.name, self.mesh)
            bpy.data.collections["Collection"].objects.link(self.mesh_obj)

        def add_geometry(self, verts: list[BM.Verts | BSM.Verts], indcs: list[int]):
            self.mesh.from_pydata([vert.geom_vert for vert in verts], [], indcs)

        def add_normals(self, verts: list[BM.Verts | BSM.Verts]):
            self.mesh.normals_split_custom_set_from_vertices([vert.norm_vert for vert in verts])

        def add_texture(self, verts: list[BM.Verts | BSM.Verts], texture_name: str):
            uv = self.mesh.uv_layers.new()
            for face in self.mesh.polygons:
                for vert, loop in zip(face.vertices, face.loop_indices):
                    uv.data[loop].uv = ( verts[vert].uv_vert[0], 1 - verts[vert].uv_vert[1] ) # V is inverted

            self.mesh.materials.append(bpy.data.materials[Path(texture_name).stem])

        def add_shapekeys(self, animations: list[BSM.Animation], verts: list[BSM.Verts]):
            sk_basis = self.mesh_obj.shape_key_add(name='Basis')
            sk_basis.interpolation = 'KEY_LINEAR'
            self.mesh_obj.data.shape_keys.use_relative = True

            prev_anim = ""
            for animation in animations:
                shape_key = self.mesh_obj.shape_key_add(name=animation.name)
                shape_key.interpolation = 'KEY_LINEAR'

                # Check the 'mof_emo##_' part of animation name, if it changes than animation is absolute
                is_absolute_animation = animation.name[0:10] != prev_anim
                prev_anim = animation.name[0:10]

                for indc, vert in zip(animation.vert_inds, animation.vert_list):
                    if is_absolute_animation:
                        shape_key.data[indc].co = vert
                    else:
                        shape_key.data[indc].co = ( \
                            verts[indc].geom_vert[0] + vert[0], \
                            verts[indc].geom_vert[1] + vert[1], \
                            verts[indc].geom_vert[2] + vert[2] )

        def add_bone_weights(self, bones: list[Tree], verts: list[BSM.Verts], mesh_bones: list[int]):
            bone_map = { } # 'Mesh scoped bone id -> bone name' mapping dictionary
            for bone_count, bone in enumerate(mesh_bones):
                bone_map[bone_count] = bones[bone].data.proper_name

            # Initialize bone_vert_groups with lists
            bone_vert_groups = {}
            for bone in bone_map.values():
                bone_vert_groups[bone] = []

            # Add tuple of (vertex number, bone weight) for both bones in vertex entry
            for vert_count, vert in enumerate(verts):
                bone_vert_groups[bone_map[vert.bone0]] += [ (vert_count, vert.bone0_weight) ]
                bone_vert_groups[bone_map[vert.bone1]] += [ (vert_count, vert.bone1_weight) ]

            for bone_key, bone_value in bone_vert_groups.items():
                vert_group = self.mesh_obj.vertex_groups.new(name=bone_key)
                for weight in bone_value:
                    vert_group.add([weight[0]], weight[1], "ADD")


    name: str
    meshes: list['BlenderModel.Mesh'] = []


    def __init__(self, name: str):
        self.name = name
        bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True) # Remove default cube

    def open(self, filepath: str):
        bpy.ops.wm.open_mainfile(filepath=str(filepath))

    def save(self, filepath: str):
        bpy.ops.wm.save_as_mainfile(filepath=str(filepath))

    def add_texture_image(self, name: str, filepath: str):
        image = bpy.data.images.load(str(filepath))
        image.pack()

        material = bpy.data.materials.new(name)
        material.use_nodes = True

        texture = material.node_tree.nodes.new('ShaderNodeTexImage')
        texture.image = image

        bsdf = material.node_tree.nodes["Principled BSDF"]
        material.node_tree.links.new(bsdf.inputs['Base Color'], texture.outputs['Color'])
        material.node_tree.links.new(bsdf.inputs['Alpha'], texture.outputs['Alpha'])
        material.blend_method = "CLIP"

    def add_mesh(self, name: str):
        mesh = BlenderModel.Mesh(name)
        self.meshes += [ mesh ]
        return mesh

    def add_armature(self, armature_tree: Tree):
        armature = bpy.data.armatures.new("Armature")
        armature_obj = bpy.data.objects.new(armature.name, armature)
        bpy.data.collections["Collection"].objects.link(armature_obj)
        bpy.context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        armature_obj.show_in_front = True

        transform_tree = Tree(armature_tree, deep=True)
        for bone_id in transform_tree.expand_tree():
            if bone_id == armature_tree.root:
                transform_tree[bone_id].data = mathutils.Matrix.Identity(4)
            else:
                transform_tree[bone_id].data = \
                    transform_tree[armature_tree.parent(bone_id).identifier].data @ mathutils.Matrix(armature_tree[bone_id].data.transform)
        for bone_id in armature_tree.expand_tree():
            if bone_id == armature_tree.root:
                continue

            bone = armature.edit_bones.new(bone_id)
            if not armature_tree[bone_id] in armature_tree.children(armature_tree.root): # If bone is not child of root
                bone.parent = armature.edit_bones[armature_tree.parent(bone_id).identifier]
            bone.transform(transform_tree[bone_id].data)
            bone.length = 0.01

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.data.meshes

        meshes = [ mesh.mesh_obj for mesh in self.meshes ]
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        for mesh in meshes:
            mesh.select_set(True)
            armature_obj.select_set(True)
            bpy.context.view_layer.objects.active = armature_obj
            bpy.ops.object.parent_set(type='ARMATURE')
            bpy.ops.object.select_all(action='DESELECT')
