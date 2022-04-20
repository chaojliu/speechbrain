"""
Data preparation.

Author
Liu Chaojie
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
SAMPLERATE = 16000

def prepare_dsing(
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

    train_folder = os.path.join(data_folder, "train30/audio")
    valid_folder = os.path.join(data_folder, "dev")
    test_folder = os.path.join(data_folder, "test")


    train_json_dict = create_json_dict(train_folder)
    create_json(train_json_dict, save_json_train)

    valid_json_dict = create_json_dict(valid_folder)
    create_json(valid_json_dict, save_json_valid)

    test_json_dict = create_json_dict(test_folder)
    create_json(test_json_dict, save_json_test)


def create_json_dict(split_folder):
    json_dict = {}
    transcription = os.path.join(split_folder, "transcription.txt")
    with open(transcription, "r") as f:
        lines = f.readlines()
        for line in lines: # skip the sync
            utter, transcript = parse_line(line)
            wav = os.path.join(split_folder, utter+".wav")
            transcript = normalize_transcript(transcript)
            json_dict[utter] = {
                "wav": wav,
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

# Keep this method in case DSing text requires extra processing.
def normalize_transcript(transcript):
    # transcript = re.sub(r'[^a-zA-Z\']', " ", transcript).upper()
    # transcript = " ".join(transcript.split())
    # Keep this method in case DSing text requires processing.
    return transcript

# Parses an annotation line.
# utter :: string
# transcript :: string
def parse_line(line):
    line = line.strip()
    tokens = line.split()
    utter = tokens[0]
    transcript = " ".join(tokens[1:])

    # left_bracket, right_bracket = line.rfind("("), line.rfind(")")
    # id = line[left_bracket + 1 : right_bracket]

    # tokens = line[:left_bracket].split()
    # start_time, end_time = float(tokens[0]), float(tokens[1])
    # transcript = " ".join(tokens[2:])
    
    return utter, transcript

if __name__ == "__main__":

    data_folder = "/data1/chaojliu/DSing"
    save_json_train = "/Users/liu/Desktop/Modules/FYP/dataset/refined_data/annotation/json/train.json"
    save_json_valid = "/Users/liu/Desktop/Modules/FYP/dataset/refined_data/annotation/json/valid.json"
    save_json_test = "/Users/liu/Desktop/Modules/FYP/dataset/refined_data/annotation/json/test.json"

    prepare_chimeesense(
        data_folder, save_json_train, save_json_valid, save_json_test
    )
