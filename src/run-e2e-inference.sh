#!/usr/bin/env bash

python src/inference.py \
        --user-input=./data/space_restoration_final.csv \
        --out-file=./data/e2e-inference-results.csv
