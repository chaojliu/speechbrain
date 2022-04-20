"""
Data preparation for the utterance-level N20EM dataset.

Author
Liu Chaojie
------

"""

import os
import json
import logging

logger = logging.getLogger(__name__)
SAMPLERATE = 44100

def prepare_n20em(
    data_folder, save_json_train, save_json_valid, save_json_test
):
    """
    Prepares the json files for the N20EM dataset.
    Arguments
    ---------
    data_folder : str
        Path to the folder where the N20EM-utterance dataset is stored.
    save_json_train : str
        Path where the train data specification file will be saved.
    save_json_valid : str
        Path where the validation data specification file will be saved.
    save_json_test : str
        Path where the test data specification file will be saved.
    Example
    -------
    >>> data_folder = '/path/to/n20em'
    >>> prepare_n20em(data_folder, 'train.json', 'valid.json', 'test.json')
    """
    
    # Check if this phase is already done (if so, skip it)
    if skip(save_json_train, save_json_valid, save_json_test):
        logger.info("Preparation completed in previous run, skipping.")
        return

    logger.info(
        f"Creating {save_json_train}, {save_json_valid}, and {save_json_test}"
    )
    print("JSON Data Preparation is running.")

    train_json_dict, valid_json_dict, test_json_dict = create_json_dict(data_folder)
    create_json(train_json_dict, save_json_train)
    create_json(valid_json_dict, save_json_valid)
    create_json(test_json_dict, save_json_test)

def create_json_dict(data_folder):
    """
    This prepares the python dictionary object from the metadata.json in n20em utterance level.
    Returns: void
    """

    # Dataset Overview: overall 4419 utterances
    # 3803 are train
    # 616 are valid 
    # No test utterances are found, so retrieve 300 from train as test utterances. 

    # For training, we have
    # 3503 for train, 616 for valid, and 300 for test.

    annotation = os.path.join(data_folder, "metadata_split_by_song.json")

    with open(annotation, "r") as f:
        json_dict = json.load(f)

    train_json_dict = {}
    valid_json_dict = {}
    test_json_dict = {}
    
    counter = 0 # we use this counter to mark the last 300 of train as the test
    for id, body in json_dict.items():
        wav = os.path.join(data_folder, id, "audio.wav") # speech audio
        imu = os.path.join(data_folder, id, "imu.csv") # imu data
        length = float(body["duration"].split(':')[1]) # duration of the audio
        words = body["lyrics"] # transcription

        if body["split"] == "train":
            counter = counter + 1
            if counter <= 3503: 
                # train
                train_json_dict[id] = {
                    "wav": wav,
                    "imu": imu,
                    "length": length,
                    "words": words
                }

            else:
                # test  
                test_json_dict[id] = {
                    "wav": wav,
                    "imu": imu,
                    "length": length,
                    "words": words
                }

        elif body["split"] == "valid":
            # valid
            valid_json_dict[id] = {
                "wav": wav,
                "imu": imu,
                "length": length,
                "words": words
            }
    
    return train_json_dict, valid_json_dict, test_json_dict

def create_json(json_dict, json_file):
    """
    Stores the python dictionary into json files.
    Returns: void
    """
    
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

# This main function will NOT be called during training.
# The training script imports the above prepare_n20em function.
# This main function is only used to genearate json annotations from terminal.
if __name__ == "__main__":

    data_folder = "/data1/chaojliu/n20em_utter"
    save_json_train = "/home/chaojliu/train.json"
    save_json_valid = "/home/chaojliu/valid.json"
    save_json_test = "/home/chaojliu/test.json"

    prepare_n20em(
        data_folder, save_json_train, save_json_valid, save_json_test
    )
