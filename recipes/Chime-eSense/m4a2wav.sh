# This file contains bash code to convert .m4a files 
# to .wav files with pcm_s32le encoding and 16kHz sampling rate

root_folder=/Users/liu/Desktop/Modules/FYP/dataset/refined_data/raw_data
spkid=M06

for f in ${root_folder}/${spkid}/*.m4a; do ffmpeg -i "$f" -c:a pcm_s32le -ar 16000 "${f/%m4a/wav}"; done