#!/bin/bash
# Patch VLR main scripts to enable debug mode and replace them in the BinDot file.
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

if [ -z "$1" ]; then
    echo "Folder path to the extracted VLR scripts required"
    exit 1
fi
INPUT=$(realpath "$1")

if [ -z "$2" ]; then
    echo "File path to ze2_data_en_us.bin required"
    exit 1
fi
BINDOT=$(realpath "$2")

if [ -z "$3" ]; then
    echo "Path to lua 5.1 x86 compiler required"
    exit 1
fi
if [ $(which $3) ]; then
    LUAC=$(which $3)
else
    LUAC=$(realpath $3)
fi
if [[ ! $(${LUAC} -v | grep "Lua 5.1") ]]; then
    echo "Bad version of lua compiler, expected 5.1"
    exit 1
fi
if [[ ! $(file ${LUAC} | grep "Intel 80386") ]]; then
    echo "Bad architecture of lua compiler, expected x86"
    exit 1
fi

# Go to script directory
DIR="$(dirname -- "${BASH_SOURCE[0]}")"
DIR="$(realpath -e -- "$DIR")"
cd ${DIR}

source .venv/bin/activate

mkdir workdir
mkdir workdir/script_bin
mkdir workdir/script_bin/ae

patch -p1 -d workdir/script_txt < file_analysis/debug_mode.diff

for FILE in "workdir/script_txt/"*.lua; do
    if [[ $FILE == "script_txt/*.lua" ]]; then break; fi

    FILE_BASE=$(basename $FILE)
    echo Converting: ${FILE_BASE}
    ${LUAC} -o /tmp/$FILE_BASE $FILE
    python lua/luac2vlr.py /tmp/$FILE_BASE workdir/script_bin/$FILE_BASE
done
for FILE in "workdir/script_txt/ae/"*.lua; do
    if [[ $FILE == "script_txt/ae/*.lua" ]]; then break; fi

    FILE_BASE=$(basename $FILE)
    echo Converting: ae/${FILE_BASE}
    ${LUAC} -o /tmp/$FILE_BASE $FILE
    python lua/luac2vlr.py /tmp/$FILE_BASE workdir/script_bin/ae/$FILE_BASE
done

rm workdir/script.zip
7z a workdir/script.zip workdir/script_bin
7z rn workdir/script.zip workdir/script_bin script
bindot/patch.py ${BINDOT} workdir/script.zip 2119833045
