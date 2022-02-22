# This file contains bash code to convert .m4a files to .wav files with pcm_s32le

root_folder=/Users/liu/Desktop/Modules/FYP/dataset/refined_data/unsegmented
spkid=F01

for f in ${root_folder}/${spkid}/*.m4a; do ffmpeg -i "$f" -c:a pcm_s32le "${f/%m4a/wav}"; done