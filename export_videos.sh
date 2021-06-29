#!/bin/sh

for i in {1..3}
do
    python3 export_videos.py "armature_${i}_9_16"
done