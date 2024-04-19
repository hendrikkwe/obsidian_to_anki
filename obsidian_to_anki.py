import argparse
import os
import re
import shutil
from pathlib import Path

import markdown
import pandas as pd

from paths_config import media_folder_anki, media_folder_obsidian, safe_at, vault

DEBUG = False


def generate_anki_deck_from_obs_file(
    md_file: str, media_folder_anki: str, media_folder_obsidian: str
):

    deck = pd.DataFrame(columns=["Question", "Answer"])

    with open(md_file, "r") as f:
        text = f.read()

    tags = find_tags(text)

    lines = text.split("\n")
    lines.append("")

    fields = ""
    i = 0
    j = 1

    while i < len(lines):
        answer = ""
        question = ""

        if lines[i].startswith("- "):

            # fill answer
            while lines[i + j].startswith("\t"):
                answer = answer + lines[i + j].lstrip("\t") + "\n\n"
                j = j + 1

            question = lines[i].lstrip("- ")
            question = markdown.markdown(question)

            # update counters
            i = i + j
            j = 1

            # if there is an answer (i.e. right formatting for question and answer)
            if answer != "":

                # answer: markdown to html
                answer = markdown.markdown(answer)

                # adapt html
                latex_symbols = find_all(answer, "$$")
                i_sym = 0
                while i_sym < len(latex_symbols):
                    answer = (
                        answer[: latex_symbols[i_sym]]
                        + "\["
                        + answer[latex_symbols[i_sym] + 2 :]
                    )
                    i_sym = i_sym + 1
                    answer = (
                        answer[: latex_symbols[i_sym]]
                        + "\]"
                        + answer[latex_symbols[i_sym] + 2 :]
                    )
                    i_sym = i_sym + 1

                # adapt html
                latex_symbols = find_all(answer, "$")
                i_sym = 0
                inc = 0
                while i_sym < len(latex_symbols):
                    answer = (
                        answer[: latex_symbols[i_sym] + inc]
                        + "\("
                        + answer[latex_symbols[i_sym] + 1 + inc :]
                    )
                    i_sym = i_sym + 1
                    inc = inc + 1
                    answer = (
                        answer[: latex_symbols[i_sym] + inc]
                        + "\)"
                        + answer[latex_symbols[i_sym] + 1 + inc :]
                    )
                    i_sym = i_sym + 1
                    inc = inc + 1

                # figures replace markdown with html

                # 1. find all figures index
                figure_start = find_all(answer, "![[")
                figure_end = []

                for i_figure_start in figure_start:
                    index = 0
                    while (
                        answer[i_figure_start + index : i_figure_start + index + 2]
                        != "]]"
                    ):
                        index = index + 1
                    figure_end.append(i_figure_start + index)
                    answer = (
                        answer[: i_figure_start + index]
                        + '">'
                        + answer[i_figure_start + index + 2 :]
                    )

                figures = {
                    answer[figure_start[k] + 3 : figure_end[k]]
                    for k in range(len(figure_start))
                }

                # 2. copy to media folder
                for figure in figures:

                    # answer = answer.replace(figure, f"from_obs_{figure}")

                    # copy to media folder
                    src = media_folder_obsidian + "/" + figure
                    dst = media_folder_anki + "/" + figure

                    shutil.copyfile(src=src, dst=dst)

                answer = answer.replace("![[", '<img src="')

                deck = pd.concat(
                    [deck, pd.DataFrame({"Question": [question], "Answer": [answer]})],
                    ignore_index=True,
                )

        else:
            i = i + 1

    deck["Tag"] = " ".join(tags)

    return deck


def find_tags(text):
    pattern = r"#\w+"
    tags = re.findall(pattern, text)
    return tags


def find_all(string, substring) -> list:
    index = 0
    indices = []
    while index < len(string):
        index = string.find(substring, index)
        if index == -1:
            return indices
        indices.append(index)
        index += len(substring)  # +1 to find the next occurrence
    return indices


def safe_deck(deck, output_file: str):

    print(f"Saving deck to {output_file}!")

    if len(deck):
        output_file_path = Path(output_file)
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        deck.to_csv(output_file, index=False, header=False, sep=";")


def find_md_files(folder):
    md_files = []

    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".md"):
                md_files.append(os.path.join(root, file))

    return md_files


def parse_inputs():
    parser = argparse.ArgumentParser(
        description="Transfer Obsidian Markdown to anki csv."
    )

    # Adding either -o or -i argument
    parser.add_argument("-o", "--folder", help="Folder path")
    parser.add_argument("-i", "--file", help="File path")

    # Parsing the input
    args = parser.parse_args()

    if not (args.folder or args.file):
        parser.error("At least one of -o or -i is required.")

    # Accessing the value
    folder = args.folder
    file = args.file

    # Your logic or function calls using the input value can go here

    if folder:
        print(f"Output folder: {folder}")
    elif file:
        print(f"Input file: {file}")

    return folder, file


if __name__ == "__main__":

    if DEBUG:
        folder = "test_anki"
        file = "test1anki"
    else:
        folder, file = parse_inputs()
        if file is not None:
            if folder is None:
                md_file = vault + "/" + file + ".md"
                full_safe_at = safe_at + "/" + file + ".csv"
            else:
                md_file = vault + "/" + folder + "/" + file + ".md"
                full_safe_at = safe_at + "/" + folder + "/" + file + ".csv"

            deck = generate_anki_deck_from_obs_file(
                md_file, media_folder_anki, media_folder_obsidian
            )
            safe_deck(deck, full_safe_at)

        elif file is None:
            # iterate over folder and subfolders
            md_files = find_md_files(vault + "/" + folder)

            print(
                20 * "-",
                f"Extracting {len(md_files)} from {folder}...",
                20 * "-",
                sep="\n",
            )

            for md_file in md_files:
                deck = generate_anki_deck_from_obs_file(
                    md_file, media_folder_anki, media_folder_obsidian
                )
                full_safe_at = (
                    safe_at + "/" + folder + md_file.split(folder)[-1][:-3] + ".csv"
                )
                safe_deck(deck, full_safe_at)

            print("Done :)")
