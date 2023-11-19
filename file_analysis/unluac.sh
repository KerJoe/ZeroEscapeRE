#!/bin/sh

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
