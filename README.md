# Zero Escape: The Nonary Games / Resource Extractor

This project aims to allow extracting resources from data files of the Zero Escape video game duology for PC.

## Environment setup

```
git clone https://github.com/KerJoe/ZeroEscapeRE.git
cd ZeroEscapeRE
python3.10 -m venv .venv # NOTE: Blender python module from PyPi is only available for fixed versions of python (As of October 2023, it's version 3.10)
source .venv/bin/activate
pip install -r requirements.txt
pip install -e `realpath helper`
```

## Model export

Run `./extract_ze2_data_en_us <path to ze2_data_en_us.bin>; ./auto_convert_ze2_models.sh` to export all character and room models from the resource file into `workdir/extracted_models` and `workdir/extracted_rooms`.

## Enable debug mode

Run `./extract_ze2_data_en_us <path to ze2_data_en_us.bin>; ./auto_decompile_lua_scripts.sh; ./enable_debug_mode_ze2.sh <path to ze2_data_en_us.bin> <path to luac version 5.1 for x86-32>` to enable the debug menu.

## License
The software is released under the GNU General Public License (GPL) which can be found in the file [`LICENSE.txt`](/LICENSE.txt) in the same directory as this file.

# Checklist

* [x] Export data from binary files
* [x] Import data to binary files

## 999: Nine Hours, Nine Persons, Nine Doors

Nothing planned for now...

## Virtues Last Reward
* [x] PACK archive decompression
* [x] LUA decompilation
* [x] Debug menu
* [x] Model Mesh Export
* [x] Model Texture Export
* [x] Model Bone Export
* [x] Model Skeletal Animation Export (WIP)
* [x] Model Facial Animation Export
* [x] Room export
* [ ] Room scene export

## Demonstration videos

### Character models with animations

<a href="https://www.youtube.com/watch?v=CX-y9TbJF-g"><img src="https://img.youtube.com/vi/CX-y9TbJF-g/0.jpg" alt="Virtue's Last Reward: Animation Export" width="300"></a>

### Debug mode

<a href="https://www.youtube.com/watch?v=knTZV8UCogE"><img src="https://img.youtube.com/vi/knTZV8UCogE/0.jpg" alt="Virtue's Last Reward: Debug Menu" width="300"></a>
