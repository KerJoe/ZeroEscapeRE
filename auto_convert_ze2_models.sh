#!/bin/bash
# Batch model converter script.
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
    echo "File path to ze2_data_en_us.bin required"
    exit 1
fi

# Go to script directory
DIR="$(dirname -- "${BASH_SOURCE[0]}")"
DIR="$(realpath -e -- "$DIR")"
cd ${DIR}

source .env/bin/activate

mkdir workdir
mkdir workdir/ze2_data_en_us
mkdir workdir/converted_models
mkdir workdir/extracted_models

python bindot/unpacker.py "$1" workdir/ze2_data_en_us

MODEL_FILES="22-1425188142/1587-131694615 22-1425188142/1588-149960206 22-1425188142/1589-492857346 22-1425188142/1590-662806346 22-1425188142/1591-689670353 22-1425188142/1592-743994043 22-1425188142/1593-1526829868 22-1425188142/1594-1611492479 22-1425188142/1595-1780513493 22-1425188142/1596-1874134169 22-1425188142/1597-1984660750 22-1425188142/1598-2076631810"

for MODEL in ${MODEL_FILES}; do
    unzip -o -C "workdir/ze2_data_en_us/${MODEL}" -d workdir/extracted_models
done

for MODEL in "workdir/extracted_models/scenes/chara/"*; do
    MODEL_BASE=$(basename ${MODEL})
    for ANIMATION in "" ${MODEL}/*.motion; do
        ANIMATION_BASE=$(basename ${ANIMATION} .motion)
        if [ -z ${ANIMATION} ]; then
            ANIMATION_BASE="base"
        fi
        python model_converter/blender_exporter.py workdir/converted_models/${MODEL_BASE}.${ANIMATION_BASE}.blend ${MODEL}/scene.bsn ${MODEL}/mdl/* ${MODEL}/tex/* ${ANIMATION}
    done
done