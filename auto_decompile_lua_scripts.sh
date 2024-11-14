#!/bin/bash
# Batch decompile main VLR scripts.
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

# Go to script directory
DIR="$(dirname -- "${BASH_SOURCE[0]}")"
DIR="$(realpath -e -- "$DIR")"
cd ${DIR}

shopt -s extglob

source .venv/bin/activate

mkdir workdir
mkdir workdir/script_txt
mkdir workdir/script_txt/ae

unzip -o "workdir/ze2_data_en_us/0-255/1-2119833045"?(.zip) -d workdir/

lua/vlr2luac.py workdir/script/cmd.lua /tmp/cmd.lua
lua/dummyout.py /tmp/cmd.lua /tmp/cmd.lua.out 42
lua/luac2vlr.py /tmp/cmd.lua.out workdir/script/cmd.lua

lua/vlr2luac.py workdir/script/start.lua /tmp/start.lua
lua/dummyout.py /tmp/start.lua /tmp/start.lua.out 4
lua/luac2vlr.py /tmp/start.lua.out workdir/script/start.lua

for FILE in "workdir/script/"*.lua; do
    if [[ $FILE == "workdir/script/*.lua" ]]; then break; fi

    FILE_BASE=$(basename ${FILE})
    echo Converting: ${FILE_BASE}
    file_analysis/unluac.sh ${FILE} > workdir/script_txt/${FILE_BASE}
done
for FILE in "workdir/script/ae/"*.lua; do
    if [[ $FILE == "workdir/script/ae/*.lua" ]]; then break; fi

    FILE_BASE=$(basename ${FILE})
    echo Converting: ae/${FILE_BASE}
    file_analysis/unluac.sh ${FILE} > workdir/script_txt/ae/${FILE_BASE}
done

patch -p1 -d workdir/script_txt < file_analysis/missing_functions.diff
