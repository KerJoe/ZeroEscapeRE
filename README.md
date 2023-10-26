# Zero Escape: The Nonary Games / Reverse Engineering

This project aims to allow extracting resources from data files of Zero Escape video game duology for PC.

## Environment setup

```
git clone https://github.com/KerJoe/ZeroEscapeRE.git
cd ZeroEscapeRE
python3.10 -m venv .env # NOTE: Blender python module from PyPi is only available for fixed versions of python (As of October 2023, it's version 3.10)
source .env/bin/activate
pip install -r requirements.txt
```

## License
The software is released under the GNU General Public License (GPL) which can be found in the file [`LICENSE.txt`](/LICENSE.txt) in the same directory as this file.

# Checklist

* [x] Export data from binary files
* [x] Import data to binary files

## 999: Nine Hours, Nine Persons, Nine Doors

Nothing planed for now...

## Virtues Last Reward
* [ ] PACK archive decompression
* [ ] LUA decompilation
* [x] Model Mesh Export
* [x] Model Texture Export
* [ ] Model Scene Export
* [x] Model Bone Export
* [ ] Model Skeletal Animation Export
* [x] Model Facial Animation Export
