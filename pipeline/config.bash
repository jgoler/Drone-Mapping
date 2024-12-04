#!/bin/bash
repo="/home/navlab/NeRF/drone_mapping/Drone-Mapping"
declare -a videos
declare -a percentages
percentages[0]="10.0"
percentages[1]="20.0"
percentages[2]="50.0"
percentages[3]="100.0"
declare -a algorithms
algorithms[0]="r"
algorithms[1]="n"
DATA="/data"
FRAMES="/data/frames"
KF="/data/keyframes"
PROCESSED="/data/processed"
