import sys, math
from pathlib import Path
from bm_converter import BM
from bsm_converter import BSM
from motion_converter import Motion

def div_to_chunks(L, n):
    """ Yield successive n-sized chunks from L """
    for i in range(0, len(L), n):
        yield L[i:i+n]

dirpath = Path("/home/misha/Documents/Projects/ZeroEscapeRE/model_converter/extracted_models/scenes/chara/zero_t/")
if len(sys.argv) >= 2:
    dirpath = Path(sys.argv[1]).absolute()
dirname = dirpath.stem

bsm_objs = {}
for bsm in (dirpath/'mdl').glob("*.bsm"):
    if bsm.stem in ['md_vestdummyShape-skin']:
        continue
    bsm_objs[bsm.stem] = BSM(bsm)
    print()

bm_objs = {}
for bm in (dirpath/'mdl').glob("*.bm"):
    if bm.stem in ['md_headShape']:
        continue
    bm_objs[bm.stem] = BM(bm)
    print()

motion_objs = {}
for motion in (dirpath).glob("*.motion"):
    #motion_objs[motion.stem] = Motion(motion)
    print()

textures_list_raw = []
for bsm in bsm_objs.values():
    for mesh in bsm.meshes:
        textures_list_raw += [ mesh.texture_name ]
for bm in bm_objs.values():
    for mesh in bm.meshes:
        textures_list_raw += [ mesh.texture_name ]
textures_list = list(set(textures_list_raw))

bones_list_raw = []
for bsm in bsm_objs.values():
    bones_list_raw += bsm.bones.bones
bones_dict = {}
for bone in bones_list_raw:
    if bone.proper_name in bones_dict.keys():
        continue
    bones_dict[bone.proper_name] = bone
bone_heir = {}
for bone in bones_dict:
    bone_heir[bone] = []
for bsm in bsm_objs.values():
    for parent in range(len(bsm.bones.bone_heir)):
        for child in bsm.bones.bone_heir[parent]:
            bone_heir[bsm.bones.bones[parent].proper_name] += [ bsm.bones.bones[child].proper_name ]

def traverse_bone_heir(bone, bone_heir_dict):
    if bone_heir[bone] != []:
        for child in bone_heir[bone]:
            bone_heir_dict[child] = {}
            traverse_bone_heir(child, bone_heir_dict[child])
parentless_bones = []
all_bone_children = []
bone_heir_dict = {}
for children in bone_heir.values():
    all_bone_children += children
for bone in bone_heir:
    if not bone in all_bone_children:
        parentless_bones += [ bone ]
for bone in parentless_bones:
    bone_heir_dict[bone] = {}
    traverse_bone_heir(bone, bone_heir_dict[bone])


import bpy
import mathutils

bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True) # Remove default cube

for image in textures_list:
    bpy.data.images.load(f"{Path(__file__).parent}/extracted_models/{Path(image).with_suffix('.dds')}").pack()

for model_name, model in bm_objs.items():
    for mesh_count, mesh in enumerate(model.meshes):
        bmesh = bpy.data.meshes.new(f"{model_name}.mesh") # Meshes after first will have ".###" automatically appended
        obj = bpy.data.objects.new(bmesh.name, bmesh)
        col = bpy.data.collections["Collection"]
        col.objects.link(obj)
        bpy.context.view_layer.objects.active = obj

        bmesh.from_pydata([vert.geom_vert for vert in mesh.verts], [], mesh.indcs)

        bmesh.normals_split_custom_set_from_vertices([vert.norm_vert for vert in mesh.verts])
        #bmesh.use_auto_smooth = True

        bmesh_uv = bmesh.uv_layers.new()
        for face in bmesh.polygons:
            for vert, loop in zip(face.vertices, face.loop_indices):
                bmesh_uv.data[loop].uv = ( mesh.verts[vert].uv_vert[0], 1 - mesh.verts[vert].uv_vert[1]) # V is inverted

        material = material = bpy.data.materials.new(Path(mesh.texture_name).stem)
        material.use_nodes = True

        texture = material.node_tree.nodes.new('ShaderNodeTexImage')
        texture.image = bpy.data.images[Path(mesh.texture_name).with_suffix('.dds').name]

        bsdf = material.node_tree.nodes["Principled BSDF"]
        material.node_tree.links.new(bsdf.inputs['Base Color'], texture.outputs['Color'])
        material.node_tree.links.new(bsdf.inputs['Alpha'], texture.outputs['Alpha'])
        material.blend_method = "CLIP"

        bmesh.materials.append(material)

for model_name, model in bsm_objs.items():
    for mesh_count, mesh in enumerate(model.meshes):
        bmesh = bpy.data.meshes.new(f"{model_name}.mesh") # Meshes after first will have ".###" automatically appended
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
        texture.image = bpy.data.images[Path(mesh.texture_name).with_suffix('.dds').name]

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
            prev_anim = animation.name[0:10]

            for ind, vert in zip(animation.vert_inds, animation.vert_list):
                if is_absolute_animation:
                    sk.data[ind].co = vert
                else:
                    sk.data[ind].co = ( mesh.verts[ind].geom_vert[0] + vert[0], mesh.verts[ind].geom_vert[1] + vert[1], mesh.verts[ind].geom_vert[2] + vert[2] )


def traverse_bone_heir(bone_heir_dict, parent=None, parent_transform=None, parent_bone=None):
    for child in bone_heir_dict.keys():
        bone = armature.edit_bones.new(child)
        if parent_bone:
            bone.parent = parent_bone
        if not parent_transform:
            parent_transform = mathutils.Matrix.Identity(4)
        child_abs_transform = parent_transform @ mathutils.Matrix(bones_dict[child].transform)
        bone.transform(child_abs_transform)
        bone.length = 0.01
        traverse_bone_heir(bone_heir_dict[child], child, child_abs_transform, bone)

armature = bpy.data.armatures.new(f"{dirname}.armature")
obj = bpy.data.objects.new(armature.name, armature)
col.objects.link(obj)
bpy.context.view_layer.objects.active = obj
bpy.ops.object.mode_set(mode='EDIT', toggle=False)
obj.show_in_front = True
traverse_bone_heir(bone_heir_dict)
bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

bpy.context.scene.render.fps = 100
bpy.ops.object.mode_set(mode='POSE')
obj = bpy.data.objects[f"{dirname}.armature"]
for bone in obj.pose.bones:
    bone.rotation_mode = "XYZ"
for dynamic in motion_objs['e00'].dynamics:
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


bpy.ops.wm.save_as_mainfile(filepath=f"{Path(__file__).parent}/converted_models/{dirname}.blend")