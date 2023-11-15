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
        class AnimatedAxis:
            timestamps: list[float]
            movements: list[float]

        class AnimatedVector:
            initial: tuple[float, float, float]
            axes: list['Motion.Dynamic.AnimatedAxis']

            def __init__(self, x: float, y: float, z: float):
                self.initial = x, y, z
                self.axes = [ Motion.Dynamic.AnimatedAxis() for _ in range(3) ]
                self.axes[0].timestamps = [ 0 ]; self.axes[1].timestamps = [ 0 ]; self.axes[2].timestamps = [ 0 ]
                self.axes[0].movements = [ x ]; self.axes[1].movements = [ y ]; self.axes[2].movements = [ z ]


        name: str
        size: AnimatedVector
        position: AnimatedVector
        rotation: AnimatedVector

        def __init__(self, data: AccUnpack):
            name_size = data.unpack("I")
            self.name = data.unpack(f"{name_size}s").decode("ascii")
            print(f"- {self.name}")

            unk9 = data.unpack("I")
            assert unk9 == 9

            vector_entry_count = data.unpack("I")
            assert vector_entry_count < 4

            self.size = Motion.Dynamic.AnimatedVector(1.0, 1.0, 1.0)
            self.position = Motion.Dynamic.AnimatedVector(0.0, 0.0, 0.0)
            self.rotation =  Motion.Dynamic.AnimatedVector(0.0, 0.0, 0.0)
            vector_list = []
            for _ in range(vector_entry_count):
                vector_number = data.unpack("I")
                if vector_number == 3:
                    self.size.initial = data.unpack("fff")
                    vector_list += [ self.size ]
                elif vector_number == 5:
                    self.position.initial = data.unpack("fff")
                    vector_list += [ self.position ]
                elif vector_number == 7:
                    self.rotation.initial = data.unpack("fff")
                    vector_list += [ self.rotation ]
                else:
                    raise Exception('Unknown .motion vector')
                data.unpack("8x")

            animation_entry_count = data.unpack("I")
            for _ in range(animation_entry_count):
                affected_vector_number = data.unpack("I")
                affected_axis_number = data.unpack("I")

                timestamp_count = data.unpack("I")
                timestamps = data.unpack_list('f', timestamp_count)
                movement_count = data.unpack("I")
                movements = data.unpack_list('f', movement_count)

                unk0_count = data.unpack("I")
                data.unpack_list('f', unk0_count)
                unk1_count = data.unpack("I")
                data.unpack_list('f', unk1_count)
                unk2_count = data.unpack("I")
                data.unpack_list('I', unk2_count)

                affected_axis_count = data.unpack("I")
                assert (affected_axis_count == 1 or affected_axis_count == 3)
                for axis_count in range(affected_axis_number, affected_axis_number+affected_axis_count):
                    axis = vector_list[affected_vector_number].axes[axis_count]
                    axis.timestamps = timestamps
                    axis.movements = [ movements[count+(axis_count-affected_axis_number)] for count in range(0, movement_count, affected_axis_count) ]


    class Morph:
        name: str
        progress: list[float]

        def __init__(self, data: AccUnpack):
            name_size = data.unpack("I")
            self.name = data.unpack(f"{name_size}s").decode("ascii")
            print(f"- {self.name}")

            progress_count = data.unpack("I")
            self.progress = data.unpack_list('f', progress_count)

    class Static:
        name: str
        transform: list[list[float]]

        def __init__(self, data: AccUnpack):
            name_size = data.unpack("I")
            self.name = data.unpack(f"{name_size}s").decode("ascii")
            print(f"- {self.name}")

            self.transform = list(div_to_chunks(data.unpack("16f"), 4))


    dynamics: list['Motion.Dynamic']
    morphs: list['Motion.Morph']
    statics: list['Motion.Static']

    def __init__(self, data_bytes: bytes):
        data = AccUnpack(data_bytes)

        data.unpack("32x")

        dynamic_amount = data.unpack("I")
        self.dynamics = []
        print(f"Animator contains {dynamic_amount} dynamic bone(s):")
        for _ in range(dynamic_amount):
            self.dynamics += [ Motion.Dynamic(data) ]

        morph_amount = data.unpack("I")
        self.morphs = []
        print(f"Animator contains {morph_amount} morph animation(s):")
        for _ in range(morph_amount):
            self.morphs += [ Motion.Morph(data) ]

        static_amount = data.unpack("I")
        self.statics = []
        print(f"Animator contains {static_amount} static bone(s):")
        for _ in range(static_amount):
            self.statics += [ Motion.Static(data) ]