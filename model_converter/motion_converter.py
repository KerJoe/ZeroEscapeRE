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


class DynamicExtra:
    def __init__(self, data, offset):
        unk0_count = unpack_acc("I", data, offset)
        unk0 = unpack_acc_list("f", data, offset, unk0_count)

        unk1_count = unpack_acc("I", data, offset)
        unk1 = unpack_acc_list("f", data, offset, unk1_count)

        unk2_count = unpack_acc("I", data, offset)
        unk2 = unpack_acc_list("I", data, offset, unk2_count)

        unpack_acc("12x", data, offset)

        unk3_count = unpack_acc("I", data, offset)
        unk3 = unpack_acc_list("f", data, offset, unk3_count)

        unk4_count = unpack_acc("I", data, offset)
        unk4 = unpack_acc_list("f", data, offset, unk4_count)

class Dynamic:
    name: str
    timestamps: list[float]
    rotations: list[float]
    extras: list[DynamicExtra]

    def __init__(self, data, offset):
        name_size = unpack_acc("I", data, offset)
        self.name = unpack_acc(f"{name_size}s", data, offset).decode("ascii")
        print (f"- {self.name}")

        unpack_acc("56x", data, offset)

        animation_amount = unpack_acc("I", data, offset)

        unpack_acc("8x", data, offset)

        timestamp_amount = unpack_acc("I", data, offset)
        self.timestamps = unpack_acc_list("f", data, offset, timestamp_amount)

        rotation_amount = unpack_acc("I", data, offset)
        self.rotations = unpack_acc_list("f", data, offset, rotation_amount)

        self.extras = []
        for _ in range(animation_amount - 1):
            self.extras += [ DynamicExtra(data, offset) ]

        unpack_acc("20x", data, offset)



filepath = "/home/misha/Documents/Projects/ZeroEscapeRE/model_converter/extracted_models/scenes/chara/phi/e02.motion"
if len(sys.argv) >= 2:
    filepath = Path(sys.argv[1]).absolute()
filename = Path(filepath).stem


offset = [0]
print(f"Loading animator {filepath}")
f = open(filepath, "rb")
data = f.read()
f.close()


unpack_acc("32x", data, offset)

dynamic_amount = unpack_acc("I", data, offset)
dynamics: list[Dynamic] = []
print (f"Animator contains {dynamic_amount} dynamic bone(s):")
for _ in range(dynamic_amount):
    dynamics += [ Dynamic(data, offset) ]


import bpy

blend_filepath = "/home/misha/Documents/Projects/ZeroEscapeRE/model_converter/converted_models/md_arm_LShape-skin.blend"
if len(sys.argv) >= 3:
    blend_filepath = Path(sys.argv[2]).absolute()
blend_filepath = Path(blend_filepath).absolute()
blend_filename = Path(blend_filepath).stem

bpy.ops.wm.open_mainfile(filepath=str(blend_filepath))

bpy.context.scene.render.fps = 100
bpy.ops.object.mode_set(mode='POSE')
obj = bpy.data.objects[f"{blend_filename}.armature"]
for bone in obj.pose.bones:
    bone.rotation_mode = "XYZ"
for dynamic in dynamics:
    if dynamic.name in obj.pose.bones:
        sub_bones = filter(lambda bone: bone.name.startswith(f"{dynamic.name}.") or bone.name == dynamic.name, obj.pose.bones)
        for sub_bone in sub_bones:
            if len(dynamic.rotations) % 3 != 0:
                print (f"Skipped {sub_bone.name}")
                break
            prev_angle = (0, 0, 0)
            for timestamp, angle in zip(dynamic.timestamps, div_to_chunks(dynamic.rotations, 3)):
                compensated_angle = [ angle[0], angle[1], angle[2] ]

                def norm_angle(angle):
                    """ Normalize angle to values between 0 and 360 """
                    return (angle if angle > 0 else 360 - (-angle % 360)) % 360

                def comp_angle(prev, next):
                    """ Rotate to 'curr' angle from 'prev' angle via the shortest path (clockwise or counterclockwise) """
                    angle_add = norm_angle(next - prev)
                    angle_sub = norm_angle(360 - angle_add)
                    if (angle_add < angle_sub):
                        return prev + angle_add
                    else:
                        return prev - angle_sub

                compensated_angle[0] = comp_angle(prev_angle[0], angle[0])
                compensated_angle[1] = comp_angle(prev_angle[1], angle[1])
                compensated_angle[2] = comp_angle(prev_angle[2], angle[2])

                assert(abs(prev_angle[0] - compensated_angle[0]) <= 180)
                assert(abs(prev_angle[1] - compensated_angle[1]) <= 180)
                assert(abs(prev_angle[2] - compensated_angle[2]) <= 180)

                sub_bone.rotation_euler = \
                    ( math.radians(compensated_angle[0]), math.radians(compensated_angle[1]), math.radians(compensated_angle[2]))
                sub_bone.keyframe_insert("rotation_euler", frame=int(timestamp*bpy.context.scene.render.fps))
                prev_angle = ( compensated_angle[0], compensated_angle[1], compensated_angle[2] )

bpy.ops.wm.save_as_mainfile(filepath=str(blend_filepath))