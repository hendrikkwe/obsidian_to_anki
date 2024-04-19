import argparse
import os
import re
import shutil
from pathlib import Path

import markdown
import pandas as pd

from paths_config import media_folder_anki, media_folder_obsidian, safe_at, vault

DEBUG = False


def parse_inputs():
    parser = argparse.ArgumentParser(description="Aggregate Anki csvs from one folder.")

    # Adding either -o or -i argument
    parser.add_argument("-o", "--folder", help="Folder path")

    # Parsing the input
    args = parser.parse_args()

    # Accessing the value
    folder = args.folder

    return folder


def find_csv_files(folder):
    csv_files = []

    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".csv"):
                csv_files.append(os.path.join(root, file))

    return csv_files


def safe_deck(deck, output_file: str):

    output_file_path = Path(output_file)
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    deck.to_csv(output_file, index=False, header=False, sep=";")


if __name__ == "__main__":

    if DEBUG:
        folder = "test_anki"
        file = "test1anki"
    else:
        folder = parse_inputs()

        deck = pd.DataFrame(columns=["Question", "Answer", "Tag"])

        csv_files = find_csv_files(safe_at + "/" + folder)

        for file in csv_files:
            print(file)
            temp = pd.read_csv(
                file, sep=";", names=["Question", "Answer", "Tag"], header=None
            )
            deck = pd.concat([deck, temp], axis=0)

        full_safe_at = safe_at + "/Full Folder " + folder + ".csv"

        safe_deck(deck, full_safe_at)
