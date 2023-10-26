import bpy, mathutils

class BlenderModel():
    class Mesh:
        mesh: bpy.types.Mesh
        mesh_obj: bpy.types.Object

        def __init__(self, name: str):
            self.mesh = bpy.data.meshes.new(f"{name}.mesh") # Meshes after first will have ".###" automatically appended
            self.mesh_obj = bpy.data.objects.new(self.mesh.name, self.mesh)
            bpy.data.collections["Collection"].objects.link(self.mesh_obj)
            bpy.context.view_layer.objects.active = self.mesh_obj

        def add_mesh(self, verts: list[(int, int, int)], indcs: list[int]):
            self.mesh.from_pydata(verts, [], indcs)

        def add_normals(self, verts: list[(int, int, int)]):
            self.mesh.normals_split_custom_set_from_vertices(verts)

        def add_texture(self, verts: list[(int, int)], material: str):
            uv = self.mesh.uv_layers.new()
            for face in self.mesh.polygons:
                for vert, loop in zip(face.vertices, face.loop_indices):
                    uv.data[loop].uv = ( verts[vert][0], 1 - verts[vert][1] ) # V is inverted

            self.mesh.materials.append(bpy.data.materials[material])

        def add_shapekeys(self):
            sk_basis = self.mesh_obj.shape_key_add(name='Basis')
            sk_basis.interpolation = 'KEY_LINEAR'
            self.mesh_obj.data.shape_keys.use_relative = True

            prev_anim = "mof_emo00_"
            for animation in self.mesh.animations:
                shape_key = self.mesh_obj.shape_key_add(name=animation.name)
                shape_key.interpolation = 'KEY_LINEAR'
                shape_key.relative_key = True

                is_absolute_animation = animation.name[0:10] != prev_anim

                for indc, vert in zip(animation.vert_inds, animation.vert_list):
                    if is_absolute_animation:
                        shape_key.data[indc].co = vert
                    else:
                        shape_key.data[indc].co = ( \
                            self.mesh.verts[indc].geom_vert[0] + vert[0], \
                            self.mesh.verts[indc].geom_vert[1] + vert[1], \
                            self.mesh.verts[indc].geom_vert[2] + vert[2] )

        def add_bone_weights(self, bones: dict[str, list[(int, int)]]):
            for bone_key, bone_value in bones.items():
                vert_group = self.mesh_obj.vertex_groups.new(name=bone_key)
                for weight in bone_value:
                    vert_group.add([weight[0]], weight[1], "ADD")

    name: str
    filepath: str


    def __init__(self, filepath: str):
        self.filepath = filepath
        bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True) # Remove default cube

    def open(self, filepath: str):
        bpy.ops.wm.open_mainfile(filepath=str(filepath))

    def save(self, filepath: str):
        bpy.ops.wm.save_as_mainfile(filepath=str(filepath))

    def add_texture_image(self, texture_name: str, filepath: str):
        image = bpy.data.images.load(str(filepath))
        image.pack()

        material = bpy.data.materials.new(texture_name)
        material.use_nodes = True

        texture = material.node_tree.nodes.new('ShaderNodeTexImage')
        texture.image = image

        bsdf = material.node_tree.nodes["Principled BSDF"]
        material.node_tree.links.new(bsdf.inputs['Base Color'], texture.outputs['Color'])
        material.node_tree.links.new(bsdf.inputs['Alpha'], texture.outputs['Alpha'])
        material.blend_method = "CLIP"

        return material

    def add_mesh(self, name: str):
        return BlenderModel.Mesh(name)

    def add_armature(self, name_tree: dict, transform_dict: dict):
        def traverse_bone_heir(name_tree: dict, parent_transform: list=None, parent: bpy.types.Bone=None):
            for child_name in name_tree:
                bone = armature.edit_bones.new(child_name)
                if parent:
                    bone.parent = parent
                if not parent_transform:
                    parent_transform = mathutils.Matrix.Identity(4)
                child_abs_transform = parent_transform @ mathutils.Matrix(transform_dict[child_name])
                bone.transform(child_abs_transform)
                bone.length = 0.01
                traverse_bone_heir(name_tree[child_name], child_abs_transform, bone)

        armature = bpy.data.armatures.new("Armature")
        obj = bpy.data.objects.new(armature.name, armature)
        bpy.data.collections["Collection"].objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        obj.show_in_front = True
        traverse_bone_heir(name_tree)
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.data.meshes
        return armature

    def parent_mesh_to_armature(self):
        objs = bpy.data.collections["Collection"].objects
        meshes = filter(lambda o: o.type == "MESH", objs)
        armature = objs["Armature"]

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        for mesh in meshes:
            mesh.select_set(True)
            armature.select_set(True)
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.parent_set(type='ARMATURE')
            bpy.ops.object.select_all(action='DESELECT')