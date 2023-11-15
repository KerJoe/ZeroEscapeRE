# Zero Escape: The Nonary Games / Reverse Engineering

This project aims to allow extracting resources from data files of the Zero Escape video game duology for PC.

## Environment setup

```
git clone https://github.com/KerJoe/ZeroEscapeRE.git
cd ZeroEscapeRE
python3.10 -m venv .env # NOTE: Blender python module from PyPi is only available for fixed versions of python (As of October 2023, it's version 3.10)
source .env/bin/activate
pip install -r requirements.txt
```

## Model export

Run `./auto_convert_ze2_models.sh <path to ze2_data_en_us.bin>` to export all character and room models from the resource file.

## License
The software is released under the GNU General Public License (GPL) which can be found in the file [`LICENSE.txt`](/LICENSE.txt) in the same directory as this file.

# Checklist

* [x] Export data from binary files
* [x] Import data to binary files

## 999: Nine Hours, Nine Persons, Nine Doors

Nothing planned for now...

## Virtues Last Reward
* [x] PACK archive decompression
* [ ] LUA decompilation
* [x] Model Mesh Export
* [x] Model Texture Export
* [x] Model Bone Export
* [x] Model Skeletal Animation Export (WIP)
* [x] Model Facial Animation Export
* [x] Room export
* [ ] Room scene export
