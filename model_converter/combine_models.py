import sys, bpy
from pathlib import Path

bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True) # Remove default cube

input_filepaths = [ "/home/misha/Documents/Projects/ZeroEscapeRE/model_converter/converted_models/md_arm_LShape-skin.blend" ]
if len(sys.argv) >= 3:
    input_filepaths = [ Path(path).absolute() for path in sys.argv[1:-1]]
input_filenames = [ Path(path).stem for path in input_filepaths ]

for input_filename, input_filepath in zip(input_filenames, input_filepaths):
    with bpy.data.libraries.load(input_filepath) as (data_from, data_to):
        data_to.objects = data_from.objects
        # for meshes in data_from[f"meshes"]
        #     bpy.context.scene.collection.objects.link
#        bpy.ops.wm.append(filepath=input_filepath/"Mesh", filename=input_filename)
        for obj in range(len(data_to.objects)):
            bpy.context.scene.collection.objects.link(data_to.objects[obj])

bpy.ops.wm.save_as_mainfile(filepath=f"{Path(__file__).parent}/converted_models/phi.blend")