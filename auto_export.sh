#!/bin/bash

DIR="$(dirname -- "${BASH_SOURCE[0]}")"
DIR="$(realpath -e -- "$DIR")"
cd ${DIR}

mkdir model_converter/converted_models
mkdir model_converter/extracted_models

mkdir extractor-compressor/ze2_data_en_us
#python extractor-compressor/extractor.py extractor/ze2_data_en_us.bin

MODEL_FILES="1587 1588 1589 1590 1591 1592 1593 1594 1595 1596 1597 1598"

for MODEL in ${MODEL_FILES}; do
    unzip -o -C "extractor-compressor/ze2_data_en_us/${MODEL}" -d model_converter/extracted_models
done

for MODEL in "model_converter/extracted_models/scenes/chara/"*; do
    python model_converter/full_export.py ${MODEL}
done