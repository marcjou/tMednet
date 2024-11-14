#!/bin/bash

source ~/anaconda3/etc/profile.d/conda.sh

conda activate tMednet

python3 /home/marcjou/Escritorio/Projects/tMednet/mhw_creator_uploader/create_maps.py -m all

conda deactivate
