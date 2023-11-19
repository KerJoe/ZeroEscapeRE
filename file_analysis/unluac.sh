#!/bin/bash
# Unluac wrapper with preconvertion of VLR to normal lua.
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
    echo "Luac file required"
    exit 1
fi

# Get script directory
DIR="$(dirname -- "${BASH_SOURCE[0]}")"
DIR="$(realpath -e -- "$DIR")"

source ${DIR}/../.env/bin/activate

python ${DIR}/../lua/vlr2luac.py $1 /tmp/$(basename $1)

java -jar ${DIR}/unluac.jar --rawstring /tmp/$(basename $1)
