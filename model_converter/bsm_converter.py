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


class BSM:
    class Verts:
        geom_vert:       (float, float, float) # 12 bytes
        norm_vert:       (float, float, float) # 12 bytes
        uv_vert:         (float, float) # 12 bytes # First value is NaN
        joint0:          int # 1 byte
        joint1:          int # 1 byte
        # 1 byte # Copy of joint0
        # 1 byte # Copy of joint0
        joint0_weight:   float # 4 bytes
        joint1_weight:   float # 4 bytes
        # 4 bytes # Copy of joint0_weight
        # 4 bytes # Copy of joint0_weight

        def __init__(self, data):
            self.geom_vert      = (data[0], data[1], data[2])
            self.norm_vert      = (data[3], data[4], data[5])
            self.uv_vert        = (data[7], data[8])
            self.joint0          = data[9]
            self.joint1          = data[10]
            self.joint0_weight   = data[13]
            self.joint1_weight   = data[14]

            assert(data[9] == data[11] == data[12])
            assert(data[13] == data[15] == data[16])
            assert(math.isnan(data[6]))

    class Bone:
        internal_name: str
        proper_name: str
        transform: list[list[float]]
        unknown: float

        def __init__(self, data, offset):
            internal_name_size = unpack_acc("I", data, offset)
            self.internal_name = unpack_acc(f"{internal_name_size}s", data, offset).decode("ascii")

            proper_name_size = unpack_acc("I", data, offset)
            self.proper_name = unpack_acc(f"{proper_name_size}s", data, offset).decode("ascii")

            self.transform = list(div_to_chunks(list(unpack_acc("16f", data, offset)), 4))

            self.unknown = unpack_acc("f", data, offset)

    class Bones:
        bones: list['BSM.Bone']
        bone_heir: list[list[int]]
        bone_heir_dict: dict

        def __init__(self, data, offset):
            bone_amount = unpack_acc("I", data, offset)
            self.bones = []
            print (f"Model contains {bone_amount} bone(s):")
            for _ in range(bone_amount):
                self.bones += [ BSM.Bone(data, offset) ]

            self.bone_heir = [[] for _ in range(bone_amount)]
            if bone_amount > 0:
                for bone in range(bone_amount):
                    bone_children = unpack_acc("I", data, offset)
                    for _ in range(bone_children):
                        self.bone_heir[bone] += [ unpack_acc("I", data, offset) ]
            else:
                unpack_acc("8x", data, offset)

            def traverse_bone_heir(pos, level, bone_heir_dict):
                print(f"{'  ' * level}{self.bones[pos].proper_name} : {self.bones[pos].internal_name}")
                if self.bone_heir[pos] != []:
                    for child in self.bone_heir[pos]:
                        bone_heir_dict[child] = {}
                        traverse_bone_heir(child, level + 1, bone_heir_dict[child])

            parentless_bones = []
            all_bone_children = []
            self.bone_heir_dict = {}
            for bone_count in range(bone_amount):
                all_bone_children += self.bone_heir[bone_count]
            for bone_count in range(bone_amount):
                if not bone_count in all_bone_children:
                    parentless_bones += [ bone_count ]
            for bone_count in parentless_bones:
                self.bone_heir_dict[bone_count] = {}
                traverse_bone_heir(bone_count, 1, self.bone_heir_dict[bone_count])


    class Animation:
        name: str
        vert_inds: list[int]
        vert_list: list[tuple[float, float, float]]

    class Mesh:
        verts: list['BSM.Verts']
        indcs: list[int]
        joints: list[int]
        texture_name: str
        has_extra_mesh: bool
        animations: list['BSM.Animation']

        def __init__(self, data, offset):
            unpack_acc("12x", data, offset)

            vert_amount = unpack_acc("I", data, offset)
            self.verts = unpack_acc_list("3f 3f 3f 4B 4f", data, offset, vert_amount, BSM.Verts)
            print (f"- {vert_amount} vertecies")

            unpack_acc("4x", data, offset)

            indc_amount = unpack_acc("I", data, offset)
            self.indcs = unpack_acc_list("hhh", data, offset, indc_amount//3)
            print (f"- {indc_amount} indices")

            joint_amount = unpack_acc("I", data, offset)
            self.joints = unpack_acc_list("I", data, offset, joint_amount)
            print (f"- {joint_amount} joint(s)")

            unpack_acc("117x", data, offset)

            texture_name_size = unpack_acc("I", data, offset)
            self.texture_name = unpack_acc(f"{texture_name_size}s", data, offset).decode("ascii")
            print (f"- Texture: {self.texture_name}")

            unpack_acc("52x", data, offset)

            self.has_extra_mesh = unpack_acc("B", data, offset)
            assert(self.has_extra_mesh < 2)
            self.has_extra_mesh = bool(self.has_extra_mesh)

            self.animations = []

    class ExtraMesh(Mesh):
        def __init__(self, data, offset, parent_texture_name):
            unpack_acc("12x", data, offset)

            vert_amount = unpack_acc("I", data, offset)
            self.verts = unpack_acc_list("3f 3f 3f 4B 4f", data, offset, vert_amount, BSM.Verts)
            print (f"- {vert_amount} vertecies")

            unpack_acc("4x", data, offset)

            indc_amount = unpack_acc("I", data, offset)
            self.indcs = unpack_acc_list("hhh", data, offset, indc_amount//3)
            print (f"- {indc_amount} indices")

            joint_amount = unpack_acc("I", data, offset)
            self.joints = unpack_acc_list("I", data, offset, joint_amount)
            print (f"- {joint_amount} joint(s)")

            unpack_acc("158x", data, offset)

            self.texture_name = parent_texture_name
            print (f"- Texture: {self.texture_name}")

            self.has_extra_mesh = False

            self.animations = []

    def __init__(self, filepath):
        offset = [0]
        print(f"Loading model {filepath}")
        with open(filepath, "rb") as f:
            data = f.read()

        mesh_amount = unpack_acc("I", data, offset)
        self.meshes: list[BSM.Mesh] = []
        print (f"Model contains {mesh_amount} mesh(es):")
        for mesh_count in range(mesh_amount):
            print (f"Mesh {mesh_count}:")
            new_mesh = BSM.Mesh(data, offset)
            self.meshes += [ new_mesh ]
            if new_mesh.has_extra_mesh:
                print (f"Extra mesh:")
                self.meshes += [ BSM.ExtraMesh(data, offset, new_mesh.texture_name) ]

        self.bones = BSM.Bones(data, offset)

        unpack_acc("48x", data, offset)

        animation_amount = unpack_acc("I", data, offset)
        print (f"Model contains {animation_amount} animation(s):")
        for _ in range(animation_amount):
            animation_mesh_amount = unpack_acc("I", data, offset)
            assert((animation_mesh_amount == mesh_amount) or (animation_mesh_amount == 0))

            for mesh_count in range(mesh_amount):
                animation = BSM.Animation()

                vert_ind_amount = unpack_acc("I", data, offset)
                animation.vert_inds = unpack_acc_list("h", data, offset, vert_ind_amount)

                vert_data_amount = unpack_acc("I", data, offset)
                animation.vert_list = unpack_acc_list("3f", data, offset, vert_data_amount)

                assert(vert_ind_amount == vert_data_amount)

                self.meshes[mesh_count].animations += [ animation ]

        animation_name_amount = unpack_acc("I", data, offset)
        assert(animation_amount == animation_name_amount)
        for animation_name_count in range(animation_name_amount):
            animation_name_size = unpack_acc("I", data, offset)
            animation_name = unpack_acc(f"{animation_name_size}s", data, offset).decode("ascii")
            for mesh in self.meshes:
                print(f"- {animation_name}")
                mesh.animations[animation_name_count].name = animation_name


if __name__ == "__main__":
    filepath = Path("/home/misha/Documents/Projects/ZeroEscapeRE/model_converter/extracted_models/scenes/chara/phi/mdl/md_arm_LShape-skin.bsm")
    if len(sys.argv) >= 2:
        filepath = Path(sys.argv[1]).absolute()
    filename = filepath.stem

    model = BSM(filepath)

    import bpy
    import mathutils

    bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True) # Remove default cube
    for mesh_count, mesh in enumerate(model.meshes):
        bmesh = bpy.data.meshes.new(f"{filename}.mesh") # Meshes after first will have ".###" automatically appended
        col = bpy.data.collections["Collection"]
        obj = bpy.data.objects.new(bmesh.name, bmesh)
        col.objects.link(obj)
        bpy.context.view_layer.objects.active = obj

        bmesh.from_pydata([vert.geom_vert for vert in mesh.verts], [], mesh.indcs)

        bmesh.normals_split_custom_set_from_vertices([vert.norm_vert for vert in mesh.verts])
        #bmesh.use_auto_smooth = True

        bmesh_uv = bmesh.uv_layers.new()
        for face in bmesh.polygons:
            for vert, loop in zip(face.vertices, face.loop_indices):
                bmesh_uv.data[loop].uv = ( mesh.verts[vert].uv_vert[0], 1 - mesh.verts[vert].uv_vert[1]) # V is inverted

        image = bpy.data.images.load(f"{Path(__file__).parent}/extracted_models/{Path(mesh.texture_name).with_suffix('.dds')}")
        image.pack()

        material = material = bpy.data.materials.new(Path(mesh.texture_name).stem)
        material.use_nodes = True

        texture = material.node_tree.nodes.new('ShaderNodeTexImage')
        texture.image = image

        bsdf = material.node_tree.nodes["Principled BSDF"]
        material.node_tree.links.new(bsdf.inputs['Base Color'], texture.outputs['Color'])
        material.node_tree.links.new(bsdf.inputs['Alpha'], texture.outputs['Alpha'])
        material.blend_method = "CLIP"

        bmesh.materials.append(material)

        joint_vert_groups = [ [] for _ in model.bones.bones ]
        for vert_count, vert in enumerate(mesh.verts):
            joint_vert_groups[mesh.joints[vert.joint0]] += [ (vert_count, vert.joint0_weight) ]
            joint_vert_groups[mesh.joints[vert.joint1]] += [ (vert_count, vert.joint1_weight) ]
        for joint in mesh.joints:
            vg = obj.vertex_groups.new(name=model.bones.bones[joint].proper_name)
            for joint_vert_group in joint_vert_groups[joint]:
                vg.add([joint_vert_group[0]], joint_vert_group[1], "ADD")

        sk_basis = obj.shape_key_add(name='Basis')
        sk_basis.interpolation = 'KEY_LINEAR'
        obj.data.shape_keys.use_relative = True

        prev_anim = "mof_emo00_"
        for animation_count, animation in enumerate(mesh.animations):
            sk = obj.shape_key_add(name=animation.name)
            sk.interpolation = 'KEY_LINEAR'

            is_absolute_animation = animation.name[0:10] != prev_anim

            for ind, vert in zip(animation.vert_inds, animation.vert_list):
                if is_absolute_animation:
                    sk.data[ind].co = vert
                else:
                    sk.data[ind].co = ( mesh.verts[ind].geom_vert[0] + vert[0], mesh.verts[ind].geom_vert[1] + vert[1], mesh.verts[ind].geom_vert[2] + vert[2] )


    def traverse_bone_heir(bone_heir_dict, parent=None, parent_transform=None, parent_bone=None):
        for child in bone_heir_dict.keys():
            bone = armature.edit_bones.new(model.bones.bones[child].proper_name)
            if parent_bone:
                bone.parent = parent_bone
            if not parent_transform:
                parent_transform = mathutils.Matrix.Identity(4)
            child_abs_transform = parent_transform @ mathutils.Matrix(model.bones.bones[child].transform)
            bone.transform(child_abs_transform)
            bone.length = 0.01
            traverse_bone_heir(bone_heir_dict[child], child, child_abs_transform, bone)

    armature = bpy.data.armatures.new(f"{filename}.armature")
    obj = bpy.data.objects.new(armature.name, armature)
    col.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    obj.show_in_front = True
    traverse_bone_heir(model.bones.bone_heir_dict)
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)


    bpy.ops.wm.save_as_mainfile(filepath=f"{Path(__file__).parent}/converted_models/{filename}.blend")