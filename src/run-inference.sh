#!/usr/bin/env bash

USER_INPUT = $1

python src/inference.py --cuda=True --user-input=$USER_INPUT --weight-path=out/weights.pt
