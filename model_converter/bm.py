# .bm (simple model file) data class.
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


class BM:
    class Verts:
        geom_vert: (float, float, float) # 12 bytes
        norm_vert: (float, float, float) # 12 bytes
        uv_vert:   (float, float)        # 12 bytes # First value is unused (NaN in character models, uninitialized in room models)

        def __init__(self, data: list[int]):
            self.geom_vert = (data[0], data[1], data[2])
            self.norm_vert = (data[3], data[4], data[5])
            self.uv_vert   = (data[7], data[8])

    class Mesh:
        verts: list['BM.Verts']
        indcs: list[(int, int, int)]
        texture_name: str

        def __init__(self, data: AccUnpack):
            data.unpack("4x")

            indc_amount = data.unpack("I")
            self.indcs = data.unpack_list("hhh", indc_amount//3)
            print (f"- {indc_amount} indices")

            vert_amount = data.unpack("I")
            self.verts = data.unpack_list("3f 3f 3f", vert_amount, BM.Verts)
            print (f"- {vert_amount} vertices")

            data.unpack("52x")

            has_texture = data.unpack("B")
            assert(has_texture < 2)
            self.texture_name = ""
            if has_texture:
                texture_name_size = data.unpack("I")
                self.texture_name = data.unpack(f"{texture_name_size}s").decode("ascii")
                print (f"- Texture: {self.texture_name}")
                data.unpack("12x")

            data.unpack("24x")


    meshes: list[Mesh]


    def __init__(self, data_bytes):
        data = AccUnpack(data_bytes)

        mesh_amount = data.unpack("I")
        self.meshes = []
        print (f"Model contains {mesh_amount} mesh(es):")
        for mesh_count in range(mesh_amount):
            print (f"Mesh {mesh_count}:")
            new_mesh = BM.Mesh(data)
            self.meshes += [ new_mesh ]