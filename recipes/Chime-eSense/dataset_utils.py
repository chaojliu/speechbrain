import torchaudio
import re
import os
from speechbrain.utils.data_utils import get_all_files

# Capitalizes and keeps only ', a-z and A-Z
def normalize_transcript(transcript):
    transcript = re.sub(r'[^a-zA-Z\']', " ", transcript).upper()
    transcript = " ".join(transcript.split())
    return transcript

# Parses an annotation line (not sync).
# id :: string
# start_time, end_time :: float
# transcript :: string
def parse_line(line):
    line = line.strip()
    left_bracket, right_bracket = line.rfind("("), line.rfind(")")
    id = line[left_bracket + 1 : right_bracket]

    tokens = line[:left_bracket].split()
    start_time, end_time = float(tokens[0]), float(tokens[1])
    transcript = " ".join(tokens[2:])
    
    return id, start_time, end_time, transcript

def _segment_wav(wav, annotation, output):

    signal, sample_rate = torchaudio.load(wav)
    
    with open(annotation, "r") as f:
        lines = f.readlines()
        for line in lines[1:]: # skip the sync
            id, start_time, end_time, _ = parse_line(line)
            if (id.startswith("0MIS")): # avoid 0MISPRON transcripts
                continue

            start_frame = round(start_time * sample_rate)
            end_frame = round(end_time * sample_rate)
            segment = signal[:, start_frame : end_frame]
            torchaudio.save(os.path.join(output, id+".wav"), segment, sample_rate)

# Segments list of wav files using annotation files.
# Segmented data are in the same folder.
def segment_wav():

    # folder for unsegmented wav and annotation text
    raw_data = "/Users/liu/Desktop/Modules/FYP/dataset/refined_data/raw_data" 

    # output folder for segmented wav
    output_folder = "/Users/liu/Desktop/Modules/FYP/dataset/refined_data/segmented"

    # selected speakers' recording will be segmented
    spkids = ["F01", "F02", "F03", "F05", "F06", "M02", "M03", "M04", "M05", "M06"]
    # spkids = ["F02", "F03", "F05", "F06", "M02", "M03", "M04", "M05", "M06"]
    

    for spkid in spkids:
        spk_folder = os.path.join(raw_data, spkid)
        text_lst = get_all_files(spk_folder, match_and=['.txt'])
        for text in text_lst:
            wav = text.replace(".txt", ".wav")
            _segment_wav(wav, text, output_folder)



if __name__ == "__main__":
   segment_wav()

    # ffmpeg -i /Users/liu/Desktop/TEST/test.wav -c:a pcm_s32le /Users/liu/Desktop/TEST/test32.wav