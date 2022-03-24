"""
Data preparation.
Extracts WSJ0 text for training LM.

Possible Future Plan: Include CHIME_ESENSE text.

Author
------
Liu Chaojie 2022

"""

import os
import re
import json
import glob
import logging
from speechbrain.utils.data_utils import get_all_files, download_file

logger = logging.getLogger(__name__)

def prepare_text(
    wsj0_folder, esense_folder, save_json_train, save_json_valid, save_json_test
):
    """
    Prepares the json files for the WSJ0 text.
    Arguments
    ---------
    wsj0_folder : str
        Path to the folder where the WSJ0 is stored.
    esense_folder : str
        Path to the folder where the Chime-eSense is stored.
    save_json_train : str
        Path where the train data specification file will be saved.
    save_json_valid : str
        Path where the validation data specification file will be saved.
    save_json_test : str
        Path where the test data specification file will be saved.
    Example
    -------
    >>> wsj0_folder = '/path/to/WSJ0'
    >>> prepare_mini_librispeech(wsj0_folder, null, 'train.json', 'valid.json', 'test.json')
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
    raw_annotation_folder = os.path.join(esense_folder, "raw_data")

    # Train: WSJ0 F01 F02 F03 M02 M03 M04
    spkids = ["F01", "F02", "F03", "M02", "M03", "M04"]
    train_json_dict = create_json_dict(spkids, raw_annotation_folder)
    # train_json_dict = create_wsj0_json_dict(wsj0_folder, existing=train_json_dict)
    create_json(train_json_dict, save_json_train)

    # Valid: F05 M05
    spkids = ["F05", "M05"]
    valid_json_dict = create_json_dict(spkids, raw_annotation_folder)
    create_json(valid_json_dict, save_json_valid)

    # Test:  F06 M06
    spkids = ["F06", "M06"]
    test_json_dict = create_json_dict(spkids, raw_annotation_folder)
    create_json(test_json_dict, save_json_test)

def create_wsj0_json_dict(wsj0_folder, json_dict={}):
    text_lst = glob.glob(
        os.path.join(wsj0_folder, "**/**/**/**/*.dot"), recursive=True
    )
    
    for text in text_lst:
        with open(text, "r") as f:
            lines = f.readlines()
            for line in lines:
                id, transcript = parse_wsj0_line(line)

                transcript = normalize_wsj0_transcript(transcript)
                json_dict[id] = {
                    "words": transcript
                }
    
    return json_dict

def create_json_dict(spkids, raw_annotation_folder):
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

                    transcript = normalize_transcript(transcript)
                    json_dict[id] = {
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

def normalize_wsj0_transcript(transcript):

    acceptable_escape = ["\%PERCENT", "\.POINT"] # To be further confirmed

    def escape_checker(token):
        if token.startswith('\\'):
            return (token in acceptable_escape)
        else: 
            return True    

    tokens = transcript.split()
    tokens = list(filter(escape_checker, tokens))

    transcript = " ".join(tokens)
    transcript = normalize_transcript(transcript)

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

def parse_wsj0_line(line):
    line = line.strip()
    left_bracket, right_bracket = line.rfind("("), line.rfind(")")
    id = line[left_bracket + 1 : right_bracket]
    transcript = line[:left_bracket].strip()

    return id, transcript


if __name__ == "__main__":

    wsj0_folder = "/data1/chaojliu/WSJ0"
    esense_folder = "/home/chaojliu/refined_data"
    save_json_train = "/home/chaojliu/speechbrain/recipes/Chime-eSense/LM/data/train.json"
    save_json_valid = "/home/chaojliu/speechbrain/recipes/Chime-eSense/LM/data/valid.json"
    save_json_test = "/home/chaojliu/speechbrain/recipes/Chime-eSense/LM/data/test.json"

    prepare_text(
        wsj0_folder, esense_folder, save_json_train, save_json_valid, save_json_test
    )
