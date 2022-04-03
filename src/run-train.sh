#!/usr/bin/env bash

# Example script for training
python src/train.py \
        --cuda=True \
        --freeze-bert=False \
        --lstm-dim=-1 \
        --seed=1 \
        --lr=5e-6 \
        --epoch=1 \
        --augment-type=all  \
        --augment-rate=0.15 \
        --alpha-sub=0.4 \
        --alpha-del=0.4 \
        --data-path=data \
        --save-path=out
