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
    echo "Folder path to extracted VLR files required"
    exit 1
fi

# Go to script directory
DIR="$(dirname -- "${BASH_SOURCE[0]}")"
DIR="$(realpath -e -- "$DIR")"
cd ${DIR}

source ../.env/bin/activate

mkdir workdir
mkdir workdir/pack

for file in $(find "$1" -type f); do
    if [[ $(head -c 4 "${file}") == 'PACK' ]]; then
        echo Extracting: ${file}
        python pack/unpacker.py "${file}" workdir/pack
    fi
done