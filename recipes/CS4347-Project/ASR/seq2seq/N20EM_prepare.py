"""
Data preparation.

Author
------

"""

import os
import re
import json
import glob
import logging
import torchaudio
from speechbrain.utils.data_utils import get_all_files, download_file
from speechbrain.dataio.dataio import read_audio

logger = logging.getLogger(__name__)
SAMPLERATE = 44100

def prepare_n20em(
    data_folder, save_json_train, save_json_valid, save_json_test
):
    """
    Prepares the json files for the Mini Librispeech dataset.
    Downloads the dataset if its not found in the `data_folder`.
    Arguments
    ---------
    data_folder : str
        Path to the folder where the Mini Librispeech dataset is stored.
    save_json_train : str
        Path where the train data specification file will be saved.
    save_json_valid : str
        Path where the validation data specification file will be saved.
    save_json_test : str
        Path where the test data specification file will be saved.
    Example
    -------
    >>> data_folder = '/path/to/mini_librispeech'
    >>> prepare_mini_librispeech(data_folder, 'train.json', 'valid.json', 'test.json')
    """
    
    # Check if this phase is already done (if so, skip it)
    if skip(save_json_train, save_json_valid, save_json_test):
        logger.info("Preparation completed in previous run, skipping.")
        return

    logger.info(
        f"Creating {save_json_train}, {save_json_valid}, and {save_json_test}"
    )
    print("JSON Data Preparation is running.")

    # e.g. data_folder = "/Users/liu/Desktop/Modules/FYP/dataset/refined_data"
    # e.g. save_json_train = "/Users/liu/Desktop/Modules/FYP/dataset/refined_data/annotation/json/train.json"
    # e.g. save_json_valid = "/Users/liu/Desktop/Modules/FYP/dataset/refined_data/annotation/json/valid.json"
    # e.g. save_json_test = "/Users/liu/Desktop/Modules/FYP/dataset/refined_data/annotation/json/test.json"
    # raw_annotation_folder = os.path.join(data_folder, "raw_data")
    # segmented_folder = os.path.join("{data_root}", "segmented")
    # we don't read audio here, this segmented_folder only fills json fields
    # {data_root} can be just the data_folder here

    # Train: F01 F02 F03 M02 M03 M04
    spkids = ["F01", "F02", "F03", "M02", "M03", "M04"]
    json_dict = create_json_dict(spkids, raw_annotation_folder, segmented_folder)
    create_json(json_dict, save_json_train)

    # Valid: F05 M05
    spkids = ["F05", "M05"]
    json_dict = create_json_dict(spkids, raw_annotation_folder, segmented_folder)
    create_json(json_dict, save_json_valid)

    # Test:  F06 M06
    spkids = ["F06", "M06"]
    json_dict = create_json_dict(spkids, raw_annotation_folder, segmented_folder)
    create_json(json_dict, save_json_test)

def create_json_dict(data_folder):
    annotation = os.path.join(data_folder, "metadata_split_by_song.json")

    # 4419 utters in total
    # 3803 of them are train
    # 616 of the are valid (so there's no test in the given n20em)
    # Therefore we use the last 300 of train as test

    # 3503 for train; 616 for valid; 300 for test.

    with open(annotation, "r") as f:
        json_dict = json.load(f)

    train_json_dict = {}
    valid_json_dict = {}
    test_json_dict = {}
    
    counter = 0
    for utter, body in json_dict.items():
        if body["split"] == "train":
            counter = counter + 1
            if counter <= 3503: 
                print("train")
                # train
            else:
                # test  
                print("test")

        elif body["split"] == "valid":
            # valid
            print(state, ":", capital)
        

    

def create_json_dict(spkids, raw_annotation_folder, segmented_folder):
    json_dict = {}
    for spkid in spkids:
        spk_folder = os.path.join(raw_annotation_folder, spkid)
        text_lst = get_all_files(spk_folder, match_and=['.txt'])
        for text in text_lst:
            with open(text, "r") as f:
                lines = f.readlines()
                for line in lines[1:]: # skip the sync
                    id, start_time, end_time, transcript = parse_line(line)
                    if (id.startswith("0MIS")): # avoid 0MISPRON transcripts
                        continue

                    wav = os.path.join(segmented_folder, id+".wav")
                    length = end_time - start_time
                    transcript = normalize_transcript(transcript)
                    json_dict[id] = {
                        "wav": wav,
                        "length": length,
                        "words": transcript
                    }
    
    return json_dict

def create_json(json_dict, json_file):

    with open(json_file, mode="w") as json_f:
        json.dump(json_dict, json_f, indent=2)

    logger.info(f"{json_file} successfully created!")

def skip(*filenames):
    """
    Detects if the data preparation has been already done.
    If the preparation has been done, we can skip it.
    Returns
    -------
    bool
        if True, the preparation phase can be skipped.
        if False, it must be done.
    """
    for filename in filenames:
        if not os.path.isfile(filename):
            return False
    return True

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

if __name__ == "__main__":

    data_folder = "/Users/liu/Desktop/Modules/FYP/dataset/refined_data"
    save_json_train = "/Users/liu/Desktop/Modules/FYP/dataset/refined_data/annotation/json/train.json"
    save_json_valid = "/Users/liu/Desktop/Modules/FYP/dataset/refined_data/annotation/json/valid.json"
    save_json_test = "/Users/liu/Desktop/Modules/FYP/dataset/refined_data/annotation/json/test.json"

    prepare_chimeesense(
        data_folder, save_json_train, save_json_valid, save_json_test
    )
