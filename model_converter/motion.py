# .motion (skeletal animation) data class.
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

from helper import *


class Motion:
    class DynamicExtra:
        def __init__(self, data: AccUnpack):
            unk0_count = data.unpack("I")
            unk0 = data.unpack_list("f", unk0_count)

            unk1_count = data.unpack("I")
            unk1 = data.unpack_list("f", unk1_count)

            unk2_count = data.unpack("I")
            unk2 = data.unpack_list("I", unk2_count)

            data.unpack("12x")

            unk3_count = data.unpack("I")
            unk3 = data.unpack_list("f", unk3_count)

            unk4_count = data.unpack("I")
            unk4 = data.unpack_list("f", unk4_count)

    class Dynamic:
        name: str
        timestamps: list[float]
        rotations: list[float]
        extras: list['Motion.DynamicExtra']

        def __init__(self, data: AccUnpack):
            name_size = data.unpack("I")
            self.name = data.unpack(f"{name_size}s").decode("ascii")
            print (f"- {self.name}")

            data.unpack("56x")

            animation_amount = data.unpack("I")

            data.unpack("8x")

            timestamp_amount = data.unpack("I")
            self.timestamps = data.unpack_list("f", timestamp_amount)

            rotation_amount = data.unpack("I")
            self.rotations = data.unpack_list("f", rotation_amount)

            self.extras = []
            for _ in range(animation_amount - 1):
                self.extras += [ Motion.DynamicExtra(data) ]

            data.unpack("8x")
            unk0_count = data.unpack("I")
            unk0 = data.unpack_list("I", unk0_count)
            data.unpack("4x")

    class Morph:
        name: str
        progress: list[float]

        def __init__(self, data: AccUnpack):
            name_size = data.unpack("I")
            self.name = data.unpack(f"{name_size}s").decode("ascii")
            print (f"- {self.name}")

            progress_count = data.unpack("I")
            self.progress = data.unpack_list('f', progress_count)

    class Static:
        name: str
        transform: list[list[float]]

        def __init__(self, data: AccUnpack):
            name_size = data.unpack("I")
            self.name = data.unpack(f"{name_size}s").decode("ascii")
            print (f"- {self.name}")

            self.transform = list(div_to_chunks(data.unpack("16f"), 4))


    dynamics: list['Motion.Dynamic']
    morphs: list['Motion.Morph']
    statics: list['Motion.Static']


    def __init__(self, data_bytes):
        data = AccUnpack(data_bytes)

        data.unpack("32x")

        dynamic_amount = data.unpack("I")
        self.dynamics = []
        print (f"Animator contains {dynamic_amount} dynamic bone(s):")
        for _ in range(dynamic_amount):
            self.dynamics += [ Motion.Dynamic(data) ]

        morph_amount = data.unpack("I")
        self.morphs = []
        print (f"Animator contains {morph_amount} morph animation(s):")
        for _ in range(morph_amount):
            self.morphs += [ Motion.Morph(data) ]

        static_amount = data.unpack("I")
        self.statics = []
        print (f"Animator contains {static_amount} static bone(s):")
        for _ in range(static_amount):
            self.statics += [ Motion.Static(data) ]