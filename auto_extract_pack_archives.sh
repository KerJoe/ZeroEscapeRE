#!/bin/bash
# Batch PACK extractor script.
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
    echo "Folder path to the extracted VLR files required"
    exit 1
fi
INPUT=$(realpath "$1")

# Go to script directory
DIR="$(dirname -- "${BASH_SOURCE[0]}")"
DIR="$(realpath -e -- "$DIR")"
cd ${DIR}

source .venv/bin/activate

mkdir workdir
mkdir workdir/pack

for FILE in $(find "${INPUT}" -type f); do
    if [[ $(head -c 4 "${FILE}") == 'PACK' ]]; then
        echo Extracting: ${FILE}
        pack/unpacker.py "${FILE}" workdir/pack
    fi
done