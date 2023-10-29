# .bsm (rigged model file) data class.
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

import math
from helper import *
from treelib import Node, Tree


class BSM:
    class Verts:
        geom_vert:    (float, float, float) # 12 bytes
        norm_vert:    (float, float, float) # 12 bytes
        uv_vert:      (float, float)        # 12 bytes # First value is NaN
        bone0:        int # 1 byte
        bone1:        int # 1 byte
        # 1 byte # Copy of bone0
        # 1 byte # Copy of bone0
        bone0_weight: float # 4 bytes
        bone1_weight: float # 4 bytes
        # 4 bytes # Copy of bone0_weight
        # 4 bytes # Copy of bone0_weight

        def __init__(self, data: list[int]):
            self.geom_vert      = (data[0], data[1], data[2])
            self.norm_vert      = (data[3], data[4], data[5])
            self.uv_vert        = (data[7], data[8])
            self.bone0          = data[9]
            self.bone1          = data[10]
            self.bone0_weight   = data[13]
            self.bone1_weight   = data[14]

            assert(data[9] == data[11] == data[12])
            assert(data[13] == data[15] == data[16])
            assert(math.isnan(data[6]))

    class Bone:
        internal_name: str
        proper_name: str
        transform: list[list[float]]

        def __init__(self, data: AccUnpack):
            internal_name_size = data.unpack("I")
            self.internal_name = data.unpack(f"{internal_name_size}s").decode("ascii")

            proper_name_size = data.unpack("I")
            self.proper_name = data.unpack(f"{proper_name_size}s").decode("ascii")

            self.transform = list(div_to_chunks(data.unpack("16f"), 4))

            self.unk0 = data.unpack("f")

    class Armature:
        bones: Tree

        def __init__(self, data: AccUnpack):
            self.bones = Tree()
            self.bones.create_node('@', '@')

            bone_amount = data.unpack("I")
            print (f"Model contains {bone_amount} bone(s):")
            for bone_count in range(bone_amount):
                # First: Create a tree of bones all parented to root
                bone = BSM.Bone(data)
                self.bones.create_node(bone.proper_name, bone_count, data=bone, parent=self.bones['@'])

            if bone_amount > 0:
                for parent in range(bone_amount):
                    bone_child_count = data.unpack("I")
                    for _ in range(bone_child_count):
                        # Second: Move bones to their parents
                        child = data.unpack("I")
                        self.bones.move_node(self.bones[child].identifier, self.bones[parent].identifier)
            else:
                data.unpack("8x")


    class Animation:
        name: str
        indcs: list[int]
        verts: list[(float, float, float)]

    class Mesh:
        verts: list['BSM.Verts']
        indcs: list[int]
        bones: list[int]
        texture_name: str
        has_extra_mesh: bool
        animations: list['BSM.Animation']

        def __init__(self, data: AccUnpack):
            data.unpack("12x")

            vert_amount = data.unpack("I")
            self.verts = data.unpack_list("3f 3f 3f 4B 4f", vert_amount, BSM.Verts)
            print (f"- {vert_amount} vertices")

            data.unpack("4x")

            indc_amount = data.unpack("I")
            self.indcs = data.unpack_list("hhh", indc_amount//3)
            print (f"- {indc_amount} indices")

            bone_amount = data.unpack("I")
            self.bones = data.unpack_list("I", bone_amount)
            print (f"- {bone_amount} bone(s)")

            data.unpack("116x")

            has_texture = data.unpack("B")
            assert(has_texture < 2)
            if has_texture:
                texture_name_size = data.unpack("I")
                self.texture_name = data.unpack(f"{texture_name_size}s").decode("ascii")
                print (f"- Texture: {self.texture_name}")
                data.unpack("12x")

            data.unpack("40x")

            self.has_extra_mesh = data.unpack("B")
            assert(self.has_extra_mesh < 2)
            self.has_extra_mesh = bool(self.has_extra_mesh)

            self.animations = []

    class ExtraMesh(Mesh):
        def __init__(self, data: AccUnpack, parent_texture_name):
            data.unpack("12x")

            vert_amount = data.unpack("I")
            self.verts = data.unpack_list("3f 3f 3f 4B 4f", vert_amount, BSM.Verts)
            print (f"- {vert_amount} vertices")

            data.unpack("4x")

            indc_amount = data.unpack("I")
            self.indcs = data.unpack_list("hhh", indc_amount//3)
            print (f"- {indc_amount} indices")

            bone_amount = data.unpack("I")
            self.bones = data.unpack_list("I", bone_amount)
            print (f"- {bone_amount} bone(s)")

            data.unpack("158x")

            self.texture_name = parent_texture_name
            print (f"- Texture: {self.texture_name}")

            self.has_extra_mesh = False

            self.animations = []


    meshes: list[Mesh]
    armature: Armature


    def __init__(self, data_bytes):
        data = AccUnpack(data_bytes)

        mesh_amount = data.unpack("I")
        self.meshes: list[BSM.Mesh] = []
        print (f"Model contains {mesh_amount} mesh(es):")
        for mesh_count in range(mesh_amount):
            print (f"Mesh {mesh_count}:")
            new_mesh = BSM.Mesh(data)
            self.meshes += [ new_mesh ]
            if new_mesh.has_extra_mesh:
                print (f"Extra mesh:")
                self.meshes += [ BSM.ExtraMesh(data, new_mesh.texture_name) ]

        self.armature = BSM.Armature(data)

        data.unpack("48x")

        animation_amount = data.unpack("I")
        print (f"Model contains {animation_amount} animation(s):")
        for _ in range(animation_amount):
            animation_mesh_amount = data.unpack("I")
            assert((animation_mesh_amount == mesh_amount) or (animation_mesh_amount == 0))

            for mesh_count in range(mesh_amount):
                animation = BSM.Animation()

                vert_ind_amount = data.unpack("I")
                animation.vert_inds = data.unpack_list("h", vert_ind_amount)

                vert_data_amount = data.unpack("I")
                animation.vert_list = data.unpack_list("3f", vert_data_amount)

                assert(vert_ind_amount == vert_data_amount)

                self.meshes[mesh_count].animations += [ animation ]

        animation_name_amount = data.unpack("I")
        assert(animation_amount == animation_name_amount)
        for animation_name_count in range(animation_name_amount):
            animation_name_size = data.unpack("I")
            animation_name = data.unpack(f"{animation_name_size}s").decode("ascii")
            for mesh in self.meshes:
                print(f"- {animation_name}")
                mesh.animations[animation_name_count].name = animation_name