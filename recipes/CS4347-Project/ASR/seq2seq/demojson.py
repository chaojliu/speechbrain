import os
import re
import json
import glob


def parse_line(line):
    line = line.strip()
    tokens = line.split()
    start_time, end_time = float(tokens[0]), float(tokens[1])
    start_time, end_time = round(start_time*1000), round(end_time*1000)
    transcript = " ".join(tokens[2:])
    
    return start_time, end_time, transcript

def create_json(json_dict, json_file):

    with open(json_file, mode="w") as json_f:
        json.dump(json_dict, json_f, indent=2)


def create_json_dict(text):
    json_dict = {"Lyrics":[]}

    with open(text, "r") as f:
        lines = f.readlines()
        for line in lines:
            start_time, end_time, transcript = parse_line(line)
            duration = end_time - start_time
            json_dict["Lyrics"].append({
                "line": transcript, 
                "duration": duration, 
                "start": start_time,
                "end": end_time})
    
    return json_dict


if __name__ == "__main__":

    text = "/Users/liu/Desktop/SunShineLyrics.txt"
    output = "/Users/liu/Desktop/SunShineLyrics.json"

    json_dict = create_json_dict(text)
    create_json(json_dict, output)

    

