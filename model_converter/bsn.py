# .bsn (3D scene file) data class.
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


class BSN:
    class MeshEntry:
        name: str
        textures: list[str]

        def __init__(self, data: AccUnpack):
            name_size = data.unpack('I')
            self.name = data.unpack(f'{name_size}s').decode("ascii")
            print(f"  - Mesh: '{self.name}':")

            data.unpack('4x')

            texture_count = data.unpack('I')
            textures = []
            for _ in range(texture_count):
                data.unpack('52x')
                has_texture = data.unpack("B")
                assert(has_texture < 2)

                if has_texture:
                    texture_name_size = data.unpack('I')
                    texture_name = data.unpack(f'{texture_name_size}s').decode("ascii")
                    textures += [ texture_name ]
                    data.unpack('12x')
                    print(f"    - Texture: {texture_name}")

    class SceneEntry:
        type_name: str
        name: str
        offset: (float, float, float)
        rotation: (float, float, float)
        size: (float, float, float)
        meshes: list['BSN.MeshEntry']

        def __init__(self, data: AccUnpack, tree: Tree, parent: Node=None):
            self.type_name = data.unpack('4s').decode("ascii")

            name_size = data.unpack('I')
            self.name = data.unpack(f'{name_size}s').decode("ascii")
            if not self.name:
                self.name = '@'

            print(f"Scene entry '{self.name}' of type '{self.type_name}':")

            assert(data.unpack('I') == 0xFFFFFFFF)

            self.offset = data.unpack('3f'); print(f"- Spacial offset: {self.offset}")
            self.rotation = data.unpack('3f'); print(f"- Rotation (degrees): {self.rotation}")
            self.size = data.unpack('3f'); print(f"- Size multiplier: {self.size}")

            data.unpack('4x')
            mesh_count = data.unpack('I')
            print(f"- Entry contains {mesh_count} mesh(es):")
            data.unpack('8x')

            self.meshes = []
            if mesh_count:
                for _ in range(mesh_count):
                    self.meshes += [ BSN.MeshEntry(data) ]
            else:
                data.unpack('4x')

            node = tree.create_node(self.name, self.name, data=self, parent=parent)

            child_count = data.unpack('I')
            for _ in range(child_count):
                BSN.SceneEntry(data, tree, node.identifier)


    scene_entries: Tree


    def __init__(self, data_bytes):
        self.scene_entries = Tree()
        data = AccUnpack(data_bytes)

        assert(data.unpack('I') == 1)

        BSN.SceneEntry(data, self.scene_entries)
        print('Final tree:')
        print(self.scene_entries.show(stdout=False))